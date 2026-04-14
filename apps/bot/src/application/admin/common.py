from uuid import UUID

from src.application.admin.dto import AdminUserDetail
from src.application.users.dto import UserProfile
from src.application.users.ports import UsersUnitOfWork
from src.application.vpn import VpnAccess
from src.application.vpn.ports import VpnAccessUnitOfWork


def sort_accesses(accesses: tuple[VpnAccess, ...]) -> tuple[VpnAccess, ...]:
    return tuple(sorted(accesses, key=lambda access: access.created_at))


async def build_admin_user_detail(
    *,
    user: UserProfile,
    vpn_access_uow: VpnAccessUnitOfWork,
    history_limit: int = 10,
) -> AdminUserDetail:
    async with vpn_access_uow:
        accesses = await vpn_access_uow.vpn_accesses.list_by_user_id(user.id)
        history = await vpn_access_uow.vpn_access_events.list_by_user_id(user.id, history_limit)
    return AdminUserDetail(
        user=user,
        vpn_accesses=sort_accesses(accesses),
        history=history,
    )


async def get_user_by_access_id(
    *,
    access_id: UUID,
    users_uow: UsersUnitOfWork,
    vpn_access_uow: VpnAccessUnitOfWork,
) -> tuple[UserProfile, VpnAccess] | None:
    async with vpn_access_uow:
        access = await vpn_access_uow.vpn_accesses.get_by_id(access_id)
    if access is None:
        return None

    async with users_uow:
        user = await users_uow.users.get_by_id(access.user_id)
    if user is None:
        return None

    return user, access
