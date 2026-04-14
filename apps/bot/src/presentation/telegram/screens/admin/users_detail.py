# ruff: noqa: RUF001

from src.application.admin.dto import AdminUserDetail
from src.presentation.telegram.datetime import format_datetime_msk, format_expiration_msk

from .users_common import (
    format_access_event,
    format_access_status,
    format_admin_user_access_block,
    resolve_display_name_from_profile,
)


def build_admin_user_detail_text(detail: AdminUserDetail) -> str:
    display_name = resolve_display_name_from_profile(detail)
    username = f"@{detail.user.username}" if detail.user.username else "—"
    premium = "✅" if detail.user.is_premium else "—"
    created_at = format_datetime_msk(detail.user.created_at)

    if detail.vpn_accesses:
        access_block = "\n\n".join(
            format_admin_user_access_block(access, number=index)
            for index, access in enumerate(detail.vpn_accesses, start=1)
        )
    else:
        access_block = "• Подписки: <b>не выданы</b>"

    return (
        f"👤 <b>{display_name}</b>\n\n"
        f"• Telegram ID: <code>{detail.user.telegram_id}</code>\n"
        f"• Username: <b>{username}</b>\n"
        f"• Premium: <b>{premium}</b>\n"
        f"• Зарегистрирован: <b>{created_at}</b>\n\n"
        f"• Подписок: <b>{len(detail.vpn_accesses)}</b>\n\n"
        f"{access_block}"
    )


def build_admin_user_access_text(detail: AdminUserDetail) -> str:
    if detail.vpn_access is None:
        return (
            "🔗 <b>Доступ пользователя</b>\n\n"
            "У этого пользователя нет активного доступа."
        )

    access = detail.vpn_access
    issued_at = format_datetime_msk(access.issued_at)
    expires_at = format_expiration_msk(access.expires_at)
    return (
        "🔗 <b>Активный доступ</b>\n\n"
        f"• Профиль: <code>{access.external_username}</code>\n"
        f"• Статус: <b>{format_access_status(access.status)}</b>\n"
        f"• Выдан: <b>{issued_at}</b>\n"
        f"• Действует до: <b>{expires_at}</b>\n"
        f"• Конфигураций: <b>{len(access.vless_links)}</b>\n\n"
        "Открыть подписку — по кнопке ниже."
    )


def build_admin_user_history_text(detail: AdminUserDetail) -> str:
    display_name = resolve_display_name_from_profile(detail)
    if detail.history:
        history_block = "\n".join(format_access_event(e) for e in detail.history)
    else:
        history_block = "• История пуста"

    return f"🕓 <b>История · {display_name}</b>\n\n{history_block}"
