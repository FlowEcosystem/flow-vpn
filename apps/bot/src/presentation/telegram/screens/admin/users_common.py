# ruff: noqa: RUF001

from src.application.admin.dto import AdminUserDetail
from src.application.users import UserSummary
from src.application.vpn import VpnAccess, VpnAccessEvent
from src.presentation.telegram.datetime import format_datetime_msk, format_expiration_msk


def format_admin_user_line(user: UserSummary) -> str:
    display_name = resolve_display_name(user)
    username = f"@{user.username}" if user.username else "—"
    premium = " ⭐" if user.is_premium else ""
    access = "🟢" if user.has_vpn_access else "⚪"
    date = format_datetime_msk(user.created_at)
    return (
        f"• <b>{display_name}</b>{premium} · {username}\n"
        f"  {access} · ID <code>{user.telegram_id}</code> · {date}"
    )


def resolve_display_name(user: UserSummary) -> str:
    parts = [p for p in (user.first_name, user.last_name) if p]
    if parts:
        return " ".join(parts)
    if user.username:
        return user.username
    return f"User {user.telegram_id}"


def resolve_display_name_from_profile(detail: AdminUserDetail) -> str:
    parts = [p for p in (detail.user.first_name, detail.user.last_name) if p]
    if parts:
        return " ".join(parts)
    if detail.user.username:
        return detail.user.username
    return f"User {detail.user.telegram_id}"


def format_admin_user_access_block(access: VpnAccess, *, number: int) -> str:
    issued_at = format_datetime_msk(access.issued_at)
    expires_at = format_expiration_msk(access.expires_at)
    return (
        f"• Подписка #{number}: <b>{format_access_status(access.status)}</b>\n"
        f"• Профиль: <code>{access.external_username}</code>\n"
        f"• Выдана: <b>{issued_at}</b>\n"
        f"• Действует до: <b>{expires_at}</b>"
    )


def format_access_event(event: VpnAccessEvent) -> str:
    created_at = format_datetime_msk(event.created_at)
    event_title = {
        "issued": "Выдан пользователем",
        "issued_by_admin": "Выдан администратором",
        "enabled_by_admin": "Включён администратором",
        "disabled_by_admin": "Отключён администратором",
        "deleted_by_user": "Удалён пользователем",
        "deleted_by_admin": "Удалён администратором",
        "reissued_by_admin": "Перевыпущен администратором",
    }.get(event.event_type, event.event_type)
    actor = f" · admin {event.actor_telegram_id}" if event.actor_telegram_id is not None else ""
    return f"• {event_title} · <b>{created_at}</b>{actor}"


def format_access_status(status: str) -> str:
    return {
        "active": "активен ✅",
        "disabled": "отключён ⛔",
    }.get(status, status)


def format_users_filter(value: object) -> str:
    return {
        "all": "все",
        "with_access": "с доступом",
        "without_access": "без доступа",
    }.get(str(value), str(value))
