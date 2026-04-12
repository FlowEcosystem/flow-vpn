# ruff: noqa: RUF001

from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from src.app.config import Settings
from src.application.users import UserProfile
from src.application.vpn import ProvisionedVpnAccess, VpnProvisioningGateway


class MarzbanVpnProvisioningGateway(VpnProvisioningGateway):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def provision_vless_access(self, user: UserProfile) -> ProvisionedVpnAccess:
        if not self._settings.marzban_is_configured:
            raise ValueError(
                "Marzban не настроен. Заполните MARZBAN_BASE_URL, "
                "MARZBAN_USERNAME и MARZBAN_PASSWORD."
            )

        username = self._build_username(user.telegram_id)

        async with httpx.AsyncClient(
            base_url=self._settings.marzban_base_url,
            timeout=15.0,
        ) as client:
            token = await self._get_admin_token(client)
            headers = {"Authorization": f"Bearer {token}"}

            existing = await self._get_user(client, headers, username)
            if existing is None:
                payload = self._build_create_payload(username, user.telegram_id)
                response = await client.post(
                    "/api/user",
                    headers=headers,
                    json=payload,
                )
                if response.status_code == httpx.codes.CONFLICT:
                    existing = await self._get_user(client, headers, username)
                else:
                    self._raise_for_status(response, "Не удалось создать пользователя в Marzban")
                    existing = response.json()

        if existing is None:
            raise RuntimeError("Marzban не вернул данные пользователя после создания доступа.")

        return self._map_access(existing)

    async def enable_vless_access(self, external_username: str) -> ProvisionedVpnAccess:
        return await self._modify_status(external_username, status="active")

    async def disable_vless_access(self, external_username: str) -> ProvisionedVpnAccess:
        return await self._modify_status(external_username, status="disabled")

    async def reissue_vless_access(self, external_username: str) -> ProvisionedVpnAccess:
        if not self._settings.marzban_is_configured:
            raise ValueError(
                "Marzban не настроен. Заполните MARZBAN_BASE_URL, "
                "MARZBAN_USERNAME и MARZBAN_PASSWORD."
            )

        async with httpx.AsyncClient(
            base_url=self._settings.marzban_base_url,
            timeout=15.0,
        ) as client:
            token = await self._get_admin_token(client)
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.post(
                f"/api/user/{external_username}/revoke_sub",
                headers=headers,
            )
            self._raise_for_status(response, "Не удалось перевыпустить доступ в Marzban")
            return self._map_access(response.json())

    async def _get_admin_token(self, client: httpx.AsyncClient) -> str:
        response = await client.post(
            "/api/admin/token",
            data={
                "username": self._settings.marzban_username,
                "password": self._settings.marzban_password,
            },
        )
        self._raise_for_status(response, "Не удалось авторизоваться в Marzban")
        payload = response.json()
        return payload["access_token"]

    async def _get_user(
        self,
        client: httpx.AsyncClient,
        headers: dict[str, str],
        username: str,
    ) -> dict[str, Any] | None:
        response = await client.get(f"/api/user/{username}", headers=headers)
        if response.status_code == httpx.codes.NOT_FOUND:
            return None

        self._raise_for_status(response, "Не удалось получить пользователя из Marzban")
        return response.json()

    def _build_create_payload(self, username: str, telegram_id: int) -> dict[str, object]:
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

    def _build_username(self, telegram_id: int) -> str:
        prefix = self._settings.marzban_user_prefix.strip().lower() or "flow"
        username = f"{prefix}_{telegram_id}"
        return username[:32]

    async def _modify_status(self, external_username: str, *, status: str) -> ProvisionedVpnAccess:
        if not self._settings.marzban_is_configured:
            raise ValueError(
                "Marzban не настроен. Заполните MARZBAN_BASE_URL, "
                "MARZBAN_USERNAME и MARZBAN_PASSWORD."
            )

        async with httpx.AsyncClient(
            base_url=self._settings.marzban_base_url,
            timeout=15.0,
        ) as client:
            token = await self._get_admin_token(client)
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.put(
                f"/api/user/{external_username}",
                headers=headers,
                json={"status": status},
            )
            self._raise_for_status(response, "Не удалось обновить статус пользователя в Marzban")
            return self._map_access(response.json())

    def _map_access(self, payload: dict[str, Any]) -> ProvisionedVpnAccess:
        issued_at_source = payload.get("sub_updated_at") or payload["created_at"]
        return ProvisionedVpnAccess(
            provider="marzban",
            status=payload["status"],
            external_username=payload["username"],
            subscription_url=payload["subscription_url"],
            vless_links=tuple(payload.get("links", [])),
            issued_at=self._parse_datetime(issued_at_source),
            expires_at=self._parse_expire(payload.get("expire")),
        )

    def _parse_datetime(self, value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def _parse_expire(self, value: int | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromtimestamp(value, tz=UTC)

    def _raise_for_status(self, response: httpx.Response, prefix: str) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail: str
            try:
                payload = response.json()
                detail = payload.get("detail", response.text)
            except ValueError:
                detail = response.text
            raise RuntimeError(f"{prefix}: {detail}") from exc
