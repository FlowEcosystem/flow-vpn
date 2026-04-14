from src.application.admin.common import build_admin_user_detail
from src.application.admin.dto import (
    AdminUserDetail,
    AdminUserSearchResult,
    AdminUsersFilter,
    AdminUsersOverview,
)
from src.application.users.ports import UsersUnitOfWork
from src.application.vpn.ports import VpnAccessUnitOfWork


async def get_admin_users_overview(
    *,
    users_uow: UsersUnitOfWork,
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

    async with users_uow:
        total_users = await users_uow.users.count_all()
        users_with_access = await users_uow.users.count_with_vpn_access()
        total_filtered = await users_uow.users.count_filtered(has_vpn_access=has_vpn_access)
        if total_filtered > 0:
            max_page = max((total_filtered - 1) // page_size, 0)
            normalized_page = min(normalized_page, max_page)
        offset = normalized_page * page_size
        recent_users = await users_uow.users.list_page(
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


async def search_admin_users(
    *,
    users_uow: UsersUnitOfWork,
    query: str,
    limit: int = 8,
) -> AdminUserSearchResult:
    async with users_uow:
        users = await users_uow.users.search(query, limit)

    return AdminUserSearchResult(
        query=query.strip(),
        users=users,
    )


async def get_admin_user_detail(
    *,
    users_uow: UsersUnitOfWork,
    vpn_access_uow: VpnAccessUnitOfWork,
    telegram_id: int,
    history_limit: int = 10,
) -> AdminUserDetail | None:
    async with users_uow:
        user = await users_uow.users.get_by_telegram_id(telegram_id)

    if user is None:
        return None

    return await build_admin_user_detail(
        user=user,
        vpn_access_uow=vpn_access_uow,
        history_limit=history_limit,
    )
