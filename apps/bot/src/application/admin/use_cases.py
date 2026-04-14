from uuid import UUID

from src.application.admin.accesses import (
    delete_admin_access,
    disable_admin_access,
    enable_admin_access,
    issue_admin_access,
    reissue_admin_access,
)
from src.application.admin.dashboard import get_admin_dashboard
from src.application.admin.dto import (
    AdminDashboard,
    AdminUserDetail,
    AdminUserSearchResult,
    AdminUsersFilter,
    AdminUsersOverview,
)
from src.application.admin.users import (
    get_admin_user_detail,
    get_admin_users_overview,
    search_admin_users,
)
from src.application.runtime.ports import RuntimeSettingsUnitOfWork
from src.application.users.ports import UsersUnitOfWork
from src.application.vpn.ports import VpnAccessUnitOfWork, VpnProvisioningGateway


class AdminService:
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

    async def get_dashboard(self) -> AdminDashboard:
        return await get_admin_dashboard(
            users_uow=self._users_uow,
            runtime_settings_uow=self._runtime_settings_uow,
        )

    async def get_users_overview(
        self,
        *,
        page: int = 0,
        page_size: int = 6,
        current_filter: AdminUsersFilter = AdminUsersFilter.ALL,
    ) -> AdminUsersOverview:
        return await get_admin_users_overview(
            users_uow=self._users_uow,
            page=page,
            page_size=page_size,
            current_filter=current_filter,
        )

    async def search_users(self, query: str, *, limit: int = 8) -> AdminUserSearchResult:
        return await search_admin_users(
            users_uow=self._users_uow,
            query=query,
            limit=limit,
        )

    async def get_user_detail(
        self, telegram_id: int, *, history_limit: int = 10
    ) -> AdminUserDetail | None:
        return await get_admin_user_detail(
            users_uow=self._users_uow,
            vpn_access_uow=self._vpn_access_uow,
            telegram_id=telegram_id,
            history_limit=history_limit,
        )

    async def issue_access(
        self,
        telegram_id: int,
        *,
        actor_telegram_id: int,
        extra_event_details: dict[str, str] | None = None,
    ) -> AdminUserDetail | None:
        return await issue_admin_access(
            users_uow=self._users_uow,
            vpn_access_uow=self._vpn_access_uow,
            provisioning_gateway=self._provisioning_gateway,
            telegram_id=telegram_id,
            actor_telegram_id=actor_telegram_id,
            extra_event_details=extra_event_details,
        )

    async def enable_access(
        self,
        access_id: UUID,
        *,
        actor_telegram_id: int,
        extra_event_details: dict[str, str] | None = None,
    ) -> AdminUserDetail | None:
        return await enable_admin_access(
            users_uow=self._users_uow,
            vpn_access_uow=self._vpn_access_uow,
            provisioning_gateway=self._provisioning_gateway,
            access_id=access_id,
            actor_telegram_id=actor_telegram_id,
            extra_event_details=extra_event_details,
        )

    async def disable_access(
        self,
        access_id: UUID,
        *,
        actor_telegram_id: int,
        extra_event_details: dict[str, str] | None = None,
    ) -> AdminUserDetail | None:
        return await disable_admin_access(
            users_uow=self._users_uow,
            vpn_access_uow=self._vpn_access_uow,
            provisioning_gateway=self._provisioning_gateway,
            access_id=access_id,
            actor_telegram_id=actor_telegram_id,
            extra_event_details=extra_event_details,
        )

    async def reissue_access(
        self,
        access_id: UUID,
        *,
        actor_telegram_id: int,
        extra_event_details: dict[str, str] | None = None,
    ) -> AdminUserDetail | None:
        return await reissue_admin_access(
            users_uow=self._users_uow,
            vpn_access_uow=self._vpn_access_uow,
            provisioning_gateway=self._provisioning_gateway,
            access_id=access_id,
            actor_telegram_id=actor_telegram_id,
            extra_event_details=extra_event_details,
        )

    async def delete_access(
        self,
        access_id: UUID,
        *,
        actor_telegram_id: int,
        extra_event_details: dict[str, str] | None = None,
    ) -> AdminUserDetail | None:
        return await delete_admin_access(
            users_uow=self._users_uow,
            vpn_access_uow=self._vpn_access_uow,
            provisioning_gateway=self._provisioning_gateway,
            access_id=access_id,
            actor_telegram_id=actor_telegram_id,
            extra_event_details=extra_event_details,
        )
