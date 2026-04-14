# ruff: noqa: RUF001

from datetime import UTC, datetime, timedelta

import httpx
import structlog

from src.app.config import Settings
from src.application.users import UserProfile
from src.application.vpn import ProvisionedVpnAccess, VpnProvisioningGateway

from .client import MarzbanApiClient

logger = structlog.get_logger(__name__)


def _compat_uuid4_hex() -> str:
    from src.infrastructure.providers import marzban as marzban_module

    return marzban_module.uuid4().hex


class MarzbanVpnProvisioningGateway(VpnProvisioningGateway):
    def __init__(self, settings: Settings) -> None:
        self._api = MarzbanApiClient(settings)

    async def provision_vless_access(
        self,
        user: UserProfile,
        subscription_number: int,
    ) -> ProvisionedVpnAccess:
        self._api.ensure_configured()

        async with self._api.build_http_client() as client:
            headers = await self._api.build_auth_headers(client)
            for attempt in range(5):
                suffix = None if attempt == 0 else _compat_uuid4_hex()[:6]
                username = self._api.build_username(
                    user,
                    subscription_number,
                    uniqueness_suffix=suffix,
                )
                payload = self._api.build_create_payload(username, user.telegram_id)
                response = await client.post("/api/user", headers=headers, json=payload)
                if response.status_code == httpx.codes.CONFLICT:
                    logger.warning(
                        "marzban_username_conflict",
                        username=username,
                        attempt=attempt,
                    )
                    continue
                self._api.raise_for_status(response, "Не удалось создать пользователя в Marzban")
                logger.info(
                    "marzban_user_provisioned",
                    username=username,
                    telegram_id=user.telegram_id,
                )
                return self._api.map_access(response.json())

        raise RuntimeError("Не удалось подобрать уникальное имя пользователя в Marzban.")

    def _build_username(
        self,
        user: UserProfile,
        subscription_number: int,
        *,
        uniqueness_suffix: str | None = None,
    ) -> str:
        return self._api.build_username(
            user,
            subscription_number,
            uniqueness_suffix=uniqueness_suffix,
        )

    async def enable_vless_access(self, external_username: str) -> ProvisionedVpnAccess:
        return await self._modify_status(external_username, status="active")

    async def disable_vless_access(self, external_username: str) -> ProvisionedVpnAccess:
        return await self._modify_status(external_username, status="disabled")

    async def extend_vless_access(
        self,
        external_username: str,
        bonus_days: int,
    ) -> ProvisionedVpnAccess:
        self._api.ensure_configured()

        async with self._api.build_http_client() as client:
            headers = await self._api.build_auth_headers(client)
            user_data = await self._api.get_user(client, headers, external_username)
            if user_data is None:
                raise RuntimeError(f"Пользователь {external_username} не найден в Marzban")

            current_expire = user_data.get("expire") or 0
            if current_expire == 0:
                raise ValueError(
                    f"Пользователь {external_username} имеет бессрочный доступ — продление не применяется."
                )
            new_expire = int(
                (
                    datetime.fromtimestamp(current_expire, tz=UTC) + timedelta(days=bonus_days)
                ).timestamp()
            )

            response = await client.put(
                f"/api/user/{external_username}",
                headers=headers,
                json={"expire": new_expire},
            )
            self._api.raise_for_status(response, "Не удалось продлить доступ в Marzban")
            logger.info(
                "marzban_access_extended",
                username=external_username,
                bonus_days=bonus_days,
                new_expire=new_expire,
            )
            return self._api.map_access(response.json())

    async def make_vless_access_infinite(self, external_username: str) -> ProvisionedVpnAccess:
        self._api.ensure_configured()

        async with self._api.build_http_client() as client:
            headers = await self._api.build_auth_headers(client)
            response = await client.put(
                f"/api/user/{external_username}",
                headers=headers,
                json={"expire": 0},
            )
            self._api.raise_for_status(response, "Не удалось установить бессрочный доступ в Marzban")
            logger.info("marzban_access_made_infinite", username=external_username)
            return self._api.map_access(response.json())

    async def reissue_vless_access(self, external_username: str) -> ProvisionedVpnAccess:
        self._api.ensure_configured()

        async with self._api.build_http_client() as client:
            headers = await self._api.build_auth_headers(client)
            response = await client.post(
                f"/api/user/{external_username}/revoke_sub",
                headers=headers,
            )
            self._api.raise_for_status(response, "Не удалось перевыпустить доступ в Marzban")
            return self._api.map_access(response.json())

    async def delete_vless_access(self, external_username: str) -> None:
        self._api.ensure_configured()

        async with self._api.build_http_client() as client:
            headers = await self._api.build_auth_headers(client)
            response = await client.delete(
                f"/api/user/{external_username}",
                headers=headers,
            )
            if response.status_code == httpx.codes.NOT_FOUND:
                return
            self._api.raise_for_status(response, "Не удалось удалить пользователя из Marzban")

    async def _modify_status(self, external_username: str, *, status: str) -> ProvisionedVpnAccess:
        self._api.ensure_configured()

        async with self._api.build_http_client() as client:
            return await self._api.modify_status(
                client,
                external_username=external_username,
                status=status,
            )
