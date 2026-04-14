# ruff: noqa: RUF001

from uuid import UUID

from src.application.runtime.ports import RuntimeSettingsUnitOfWork
from src.application.users.ports import UsersUnitOfWork
from src.application.vpn.accesses import delete_user_access, disable_user_access, enable_user_access
from src.application.vpn.acquire import acquire_vpn_access
from src.application.vpn.dto import AcquireVpnAccessResult, VpnAccess
from src.application.vpn.expiration import expire_vpn_accesses
from src.application.vpn.ports import VpnAccessUnitOfWork, VpnProvisioningGateway


class VpnService:
    def __init__(
        self,
        users_uow: UsersUnitOfWork,
        runtime_settings_uow: RuntimeSettingsUnitOfWork,
        vpn_access_uow: VpnAccessUnitOfWork,
        provisioning_gateway: VpnProvisioningGateway,
    ) -> None:
        self._users_uow = users_uow
        self._runtime_settings_uow = runtime_settings_uow
        self._vpn_access_uow = vpn_access_uow
        self._provisioning_gateway = provisioning_gateway

    async def acquire(self, telegram_id: int) -> AcquireVpnAccessResult:
        return await acquire_vpn_access(
            users_uow=self._users_uow,
            runtime_settings_uow=self._runtime_settings_uow,
            vpn_access_uow=self._vpn_access_uow,
            provisioning_gateway=self._provisioning_gateway,
            telegram_id=telegram_id,
        )

    async def enable(self, telegram_id: int, access_id: UUID) -> VpnAccess | None:
        return await enable_user_access(
            users_uow=self._users_uow,
            vpn_access_uow=self._vpn_access_uow,
            provisioning_gateway=self._provisioning_gateway,
            telegram_id=telegram_id,
            access_id=access_id,
        )

    async def disable(self, telegram_id: int, access_id: UUID) -> VpnAccess | None:
        return await disable_user_access(
            users_uow=self._users_uow,
            vpn_access_uow=self._vpn_access_uow,
            provisioning_gateway=self._provisioning_gateway,
            telegram_id=telegram_id,
            access_id=access_id,
        )

    async def delete(self, telegram_id: int, access_id: UUID) -> bool:
        return await delete_user_access(
            users_uow=self._users_uow,
            vpn_access_uow=self._vpn_access_uow,
            provisioning_gateway=self._provisioning_gateway,
            telegram_id=telegram_id,
            access_id=access_id,
        )

    async def expire_accesses(self) -> int:
        return await expire_vpn_accesses(vpn_access_uow=self._vpn_access_uow)
