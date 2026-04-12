from datetime import UTC, datetime, time

from src.application.admin.dto import (
    AdminDashboard,
    AdminUserDetail,
    AdminUserSearchResult,
    AdminUsersFilter,
    AdminUsersOverview,
)
from src.application.runtime.ports import RuntimeSettingsUnitOfWork
from src.application.users.ports import UsersUnitOfWork
from src.application.vpn import (
    NewVpnAccessData,
    NewVpnAccessEventData,
    UpdateVpnAccessData,
)
from src.application.vpn.ports import VpnAccessUnitOfWork, VpnProvisioningGateway


class GetAdminDashboardUseCase:
    def __init__(
        self,
        users_uow: UsersUnitOfWork,
        runtime_settings_uow: RuntimeSettingsUnitOfWork,
    ) -> None:
        self._users_uow = users_uow
        self._runtime_settings_uow = runtime_settings_uow

    async def execute(self) -> AdminDashboard:
        today_started_at = datetime.combine(
            datetime.now(UTC).date(),
            time.min,
            tzinfo=UTC,
        )

        async with self._users_uow:
            total_users = await self._users_uow.users.count_all()
            new_users_today = await self._users_uow.users.count_created_since(today_started_at)
            premium_users = await self._users_uow.users.count_premium()

        async with self._runtime_settings_uow:
            access_mode = await self._runtime_settings_uow.settings.get_access_mode()

        return AdminDashboard(
            access_mode=access_mode,
            total_users=total_users,
            new_users_today=new_users_today,
            premium_users=premium_users,
        )


class GetAdminUsersOverviewUseCase:
    def __init__(self, users_uow: UsersUnitOfWork) -> None:
        self._users_uow = users_uow

    async def execute(
        self,
        *,
        page: int = 0,
        page_size: int = 6,
        current_filter: AdminUsersFilter = AdminUsersFilter.ALL,
    ) -> AdminUsersOverview:
        normalized_page = max(page, 0)
        has_vpn_access = {
            AdminUsersFilter.ALL: None,
            AdminUsersFilter.WITH_ACCESS: True,
            AdminUsersFilter.WITHOUT_ACCESS: False,
        }[current_filter]
        offset = normalized_page * page_size

        async with self._users_uow:
            total_users = await self._users_uow.users.count_all()
            users_with_access = await self._users_uow.users.count_with_vpn_access()
            total_filtered = await self._users_uow.users.count_filtered(
                has_vpn_access=has_vpn_access
            )
            recent_users = await self._users_uow.users.list_page(
                limit=page_size,
                offset=offset,
                has_vpn_access=has_vpn_access,
            )

        return AdminUsersOverview(
            total_users=total_users,
            users_with_access=users_with_access,
            total_filtered=total_filtered,
            current_page=normalized_page,
            has_next_page=offset + len(recent_users) < total_filtered,
            current_filter=current_filter,
            recent_users=recent_users,
        )


class SearchAdminUsersUseCase:
    def __init__(self, users_uow: UsersUnitOfWork) -> None:
        self._users_uow = users_uow

    async def execute(self, query: str, *, limit: int = 8) -> AdminUserSearchResult:
        async with self._users_uow:
            users = await self._users_uow.users.search(query, limit)

        return AdminUserSearchResult(
            query=query.strip(),
            users=users,
        )


class GetAdminUserDetailUseCase:
    def __init__(
        self,
        users_uow: UsersUnitOfWork,
        vpn_access_uow: VpnAccessUnitOfWork,
    ) -> None:
        self._users_uow = users_uow
        self._vpn_access_uow = vpn_access_uow

    async def execute(self, telegram_id: int, *, history_limit: int = 10) -> AdminUserDetail | None:
        async with self._users_uow:
            user = await self._users_uow.users.get_by_telegram_id(telegram_id)

        if user is None:
            return None

        async with self._vpn_access_uow:
            vpn_access = await self._vpn_access_uow.vpn_accesses.get_by_user_id(user.id)
            history = await self._vpn_access_uow.vpn_access_events.list_by_user_id(
                user.id,
                history_limit,
            )

        return AdminUserDetail(
            user=user,
            vpn_access=vpn_access,
            history=history,
        )


class IssueAdminVpnAccessUseCase:
    def __init__(
        self,
        users_uow: UsersUnitOfWork,
        vpn_access_uow: VpnAccessUnitOfWork,
        provisioning_gateway: VpnProvisioningGateway,
    ) -> None:
        self._users_uow = users_uow
        self._vpn_access_uow = vpn_access_uow
        self._provisioning_gateway = provisioning_gateway

    async def execute(self, telegram_id: int, *, actor_telegram_id: int) -> AdminUserDetail | None:
        async with self._users_uow:
            user = await self._users_uow.users.get_by_telegram_id(telegram_id)

        if user is None:
            return None

        async with self._vpn_access_uow:
            access = await self._vpn_access_uow.vpn_accesses.get_by_user_id(user.id)

        if access is None:
            provisioned = await self._provisioning_gateway.provision_vless_access(user)
            async with self._vpn_access_uow:
                access = await self._vpn_access_uow.vpn_accesses.create(
                    NewVpnAccessData(
                        user_id=user.id,
                        provider=provisioned.provider,
                        status=provisioned.status,
                        external_username=provisioned.external_username,
                        subscription_url=provisioned.subscription_url,
                        vless_links=provisioned.vless_links,
                        issued_at=provisioned.issued_at,
                        expires_at=provisioned.expires_at,
                    )
                )
                await self._vpn_access_uow.vpn_access_events.create(
                    NewVpnAccessEventData(
                        user_id=user.id,
                        access_id=access.id,
                        event_type="issued_by_admin",
                        actor_telegram_id=actor_telegram_id,
                        details={},
                    )
                )
                history = await self._vpn_access_uow.vpn_access_events.list_by_user_id(user.id, 10)
                await self._vpn_access_uow.commit()
            return AdminUserDetail(user=user, vpn_access=access, history=history)

        if access.status != "active":
            provisioned = await self._provisioning_gateway.enable_vless_access(
                access.external_username
            )
            async with self._vpn_access_uow:
                access = await self._vpn_access_uow.vpn_accesses.update(
                    access.id,
                    UpdateVpnAccessData(
                        status=provisioned.status,
                        subscription_url=provisioned.subscription_url,
                        vless_links=provisioned.vless_links,
                        issued_at=provisioned.issued_at,
                        expires_at=provisioned.expires_at,
                    ),
                )
                await self._vpn_access_uow.vpn_access_events.create(
                    NewVpnAccessEventData(
                        user_id=user.id,
                        access_id=access.id,
                        event_type="enabled_by_admin",
                        actor_telegram_id=actor_telegram_id,
                        details={},
                    )
                )
                history = await self._vpn_access_uow.vpn_access_events.list_by_user_id(user.id, 10)
                await self._vpn_access_uow.commit()
            return AdminUserDetail(user=user, vpn_access=access, history=history)

        async with self._vpn_access_uow:
            history = await self._vpn_access_uow.vpn_access_events.list_by_user_id(user.id, 10)
        return AdminUserDetail(user=user, vpn_access=access, history=history)


class DisableAdminVpnAccessUseCase:
    def __init__(
        self,
        users_uow: UsersUnitOfWork,
        vpn_access_uow: VpnAccessUnitOfWork,
        provisioning_gateway: VpnProvisioningGateway,
    ) -> None:
        self._users_uow = users_uow
        self._vpn_access_uow = vpn_access_uow
        self._provisioning_gateway = provisioning_gateway

    async def execute(self, telegram_id: int, *, actor_telegram_id: int) -> AdminUserDetail | None:
        async with self._users_uow:
            user = await self._users_uow.users.get_by_telegram_id(telegram_id)

        if user is None:
            return None

        async with self._vpn_access_uow:
            access = await self._vpn_access_uow.vpn_accesses.get_by_user_id(user.id)

        if access is None:
            return AdminUserDetail(user=user, vpn_access=None, history=())

        provisioned = await self._provisioning_gateway.disable_vless_access(
            access.external_username
        )
        async with self._vpn_access_uow:
            access = await self._vpn_access_uow.vpn_accesses.update(
                access.id,
                UpdateVpnAccessData(
                    status=provisioned.status,
                    subscription_url=provisioned.subscription_url,
                    vless_links=provisioned.vless_links,
                    issued_at=provisioned.issued_at,
                    expires_at=provisioned.expires_at,
                ),
            )
            await self._vpn_access_uow.vpn_access_events.create(
                NewVpnAccessEventData(
                    user_id=user.id,
                    access_id=access.id,
                    event_type="disabled_by_admin",
                    actor_telegram_id=actor_telegram_id,
                    details={},
                )
            )
            history = await self._vpn_access_uow.vpn_access_events.list_by_user_id(user.id, 10)
            await self._vpn_access_uow.commit()

        return AdminUserDetail(user=user, vpn_access=access, history=history)


class ReissueAdminVpnAccessUseCase:
    def __init__(
        self,
        users_uow: UsersUnitOfWork,
        vpn_access_uow: VpnAccessUnitOfWork,
        provisioning_gateway: VpnProvisioningGateway,
    ) -> None:
        self._users_uow = users_uow
        self._vpn_access_uow = vpn_access_uow
        self._provisioning_gateway = provisioning_gateway

    async def execute(self, telegram_id: int, *, actor_telegram_id: int) -> AdminUserDetail | None:
        async with self._users_uow:
            user = await self._users_uow.users.get_by_telegram_id(telegram_id)

        if user is None:
            return None

        async with self._vpn_access_uow:
            access = await self._vpn_access_uow.vpn_accesses.get_by_user_id(user.id)

        if access is None:
            return AdminUserDetail(user=user, vpn_access=None, history=())

        provisioned = await self._provisioning_gateway.reissue_vless_access(
            access.external_username
        )
        async with self._vpn_access_uow:
            access = await self._vpn_access_uow.vpn_accesses.update(
                access.id,
                UpdateVpnAccessData(
                    status=provisioned.status,
                    subscription_url=provisioned.subscription_url,
                    vless_links=provisioned.vless_links,
                    issued_at=provisioned.issued_at,
                    expires_at=provisioned.expires_at,
                ),
            )
            await self._vpn_access_uow.vpn_access_events.create(
                NewVpnAccessEventData(
                    user_id=user.id,
                    access_id=access.id,
                    event_type="reissued_by_admin",
                    actor_telegram_id=actor_telegram_id,
                    details={},
                )
            )
            history = await self._vpn_access_uow.vpn_access_events.list_by_user_id(user.id, 10)
            await self._vpn_access_uow.commit()

        return AdminUserDetail(user=user, vpn_access=access, history=history)
