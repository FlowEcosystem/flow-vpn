# ruff: noqa: RUF001

import re
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import structlog

from src.app.config import Settings
from src.application.users import UserProfile
from src.application.vpn import ProvisionedVpnAccess

logger = structlog.get_logger(__name__)


class MarzbanApiClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def ensure_configured(self) -> None:
        if not self._settings.marzban_is_configured:
            raise ValueError(
                "Marzban не настроен. Заполните MARZBAN_BASE_URL, "
                "MARZBAN_USERNAME и MARZBAN_PASSWORD."
            )

    def build_http_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._settings.marzban_base_url,
            timeout=15.0,
        )

    async def get_admin_token(self, client: httpx.AsyncClient) -> str:
        response = await client.post(
            "/api/admin/token",
            data={
                "username": self._settings.marzban_username,
                "password": self._settings.marzban_password,
            },
        )
        self.raise_for_status(response, "Не удалось авторизоваться в Marzban")
        payload = response.json()
        return payload["access_token"]

    async def build_auth_headers(self, client: httpx.AsyncClient) -> dict[str, str]:
        token = await self.get_admin_token(client)
        return {"Authorization": f"Bearer {token}"}

    async def get_user(
        self,
        client: httpx.AsyncClient,
        headers: dict[str, str],
        username: str,
    ) -> dict[str, Any] | None:
        response = await client.get(f"/api/user/{username}", headers=headers)
        if response.status_code == httpx.codes.NOT_FOUND:
            return None

        self.raise_for_status(response, "Не удалось получить пользователя из Marzban")
        return response.json()

    async def modify_status(
        self,
        client: httpx.AsyncClient,
        *,
        external_username: str,
        status: str,
    ) -> ProvisionedVpnAccess:
        headers = await self.build_auth_headers(client)
        response = await client.put(
            f"/api/user/{external_username}",
            headers=headers,
            json={"status": status},
        )
        self.raise_for_status(response, "Не удалось обновить статус пользователя в Marzban")
        payload = response.json()
        refreshed = await self.get_user(client, headers, external_username)
        if refreshed is not None:
            payload = refreshed

        access = self.map_access(payload)
        if access.status != status:
            logger.warning(
                "marzban_status_mismatch_after_update",
                username=external_username,
                requested_status=status,
                returned_status=access.status,
            )
            access = replace(access, status=status)

        return access

    def build_create_payload(self, username: str, telegram_id: int) -> dict[str, object]:
        expire = 0
        if self._settings.marzban_free_access_expire_days > 0:
            expire_dt = datetime.now(UTC) + timedelta(
                days=self._settings.marzban_free_access_expire_days,
            )
            expire = int(expire_dt.timestamp())

        payload: dict[str, object] = {
            "username": username,
            "status": "active",
            "expire": expire,
            "data_limit": self._settings.marzban_free_access_data_limit_bytes,
            "data_limit_reset_strategy": "no_reset",
            "proxies": {"vless": {}},
            "inbounds": {},
            "note": f"telegram_id={telegram_id}",
        }
        if self._settings.marzban_vless_inbounds:
            payload["inbounds"] = {"vless": list(self._settings.marzban_vless_inbounds)}
        return payload

    def build_username(
        self,
        user: UserProfile,
        subscription_number: int,
        *,
        uniqueness_suffix: str | None = None,
    ) -> str:
        base = self.normalize_username(user.username, user.telegram_id)
        tail_parts = [str(subscription_number)]
        if uniqueness_suffix is not None:
            tail_parts.append(uniqueness_suffix)

        tail = "_".join(tail_parts)
        max_base_len = max(1, 32 - len(tail) - 1)
        return f"{base[:max_base_len]}_{tail}"

    def normalize_username(self, username: str | None, telegram_id: int) -> str:
        candidate = (username or f"tg_{telegram_id}").strip().lower().removeprefix("@")
        normalized = re.sub(r"[^a-z0-9_]+", "_", candidate).strip("_")
        return normalized or f"tg_{telegram_id}"

    def map_access(self, payload: dict[str, Any]) -> ProvisionedVpnAccess:
        issued_at_source = payload.get("sub_updated_at") or payload["created_at"]
        return ProvisionedVpnAccess(
            provider="marzban",
            status=payload["status"],
            external_username=payload["username"],
            subscription_url=payload["subscription_url"],
            vless_links=tuple(payload.get("links", [])),
            issued_at=self.parse_datetime(issued_at_source),
            expires_at=self.parse_expire(payload.get("expire")),
        )

    def parse_datetime(self, value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def parse_expire(self, value: int | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromtimestamp(value, tz=UTC)

    def raise_for_status(self, response: httpx.Response, prefix: str) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail: str
            try:
                payload = response.json()
                detail = payload.get("detail", response.text)
            except ValueError:
                detail = response.text
            logger.error(
                "marzban_http_error",
                status_code=response.status_code,
                url=str(response.request.url),
                detail=detail,
            )
            raise RuntimeError(f"{prefix}: {detail}") from exc
