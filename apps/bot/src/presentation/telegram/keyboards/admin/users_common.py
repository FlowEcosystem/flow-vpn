# ruff: noqa: RUF001

from src.application.admin import AdminUsersFilter
from src.application.users import UserSummary


def build_user_button_label(user: UserSummary) -> str:
    status_icon = "🟢" if user.has_vpn_access else "⚪"
    if user.first_name:
        name = user.first_name
    elif user.username:
        name = f"@{user.username}"
    else:
        name = f"ID {user.telegram_id}"
    return f"{status_icon} {name[:18]} · {user.telegram_id}"


def build_filter_label(
    target_filter: AdminUsersFilter,
    current_filter: AdminUsersFilter,
) -> str:
    label = {
        AdminUsersFilter.ALL: "Все",
        AdminUsersFilter.WITH_ACCESS: "С доступом",
        AdminUsersFilter.WITHOUT_ACCESS: "Без доступа",
    }[target_filter]
    prefix = "🟢 " if target_filter is current_filter else "⚪ "
    return f"{prefix}{label}"
