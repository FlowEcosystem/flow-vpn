from datetime import UTC, datetime, time

from src.application.admin.dto import AdminDashboard
from src.application.runtime.ports import RuntimeSettingsUnitOfWork
from src.application.users.ports import UsersUnitOfWork


async def get_admin_dashboard(
    *,
    users_uow: UsersUnitOfWork,
    runtime_settings_uow: RuntimeSettingsUnitOfWork,
) -> AdminDashboard:
    today_started_at = datetime.combine(
        datetime.now(UTC).date(),
        time.min,
        tzinfo=UTC,
    )

    async with users_uow:
        total_users = await users_uow.users.count_all()
        new_users_today = await users_uow.users.count_created_since(today_started_at)
        premium_users = await users_uow.users.count_premium()

    async with runtime_settings_uow:
        access_mode = await runtime_settings_uow.settings.get_access_mode()
        max_vpn_accesses_per_user = (
            await runtime_settings_uow.settings.get_max_vpn_accesses_per_user()
        )

    return AdminDashboard(
        access_mode=access_mode,
        max_vpn_accesses_per_user=max_vpn_accesses_per_user,
        total_users=total_users,
        new_users_today=new_users_today,
        premium_users=premium_users,
    )
