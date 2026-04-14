# ruff: noqa: RUF001

from src.application.admin.dto import AdminUserSearchResult, AdminUsersOverview

from .users_common import format_admin_user_line, format_users_filter


def build_admin_users_text(overview: AdminUsersOverview) -> str:
    if overview.recent_users:
        users_block = "\n".join(format_admin_user_line(u) for u in overview.recent_users)
    else:
        users_block = "• Пользователей нет"

    without_access = overview.total_users - overview.users_with_access
    filter_label = format_users_filter(overview.current_filter)

    return (
        "👥 <b>Пользователи</b>\n\n"
        f"• Всего: <b>{overview.total_users:,}</b>"
        f" · С доступом: <b>{overview.users_with_access}</b>"
        f" · Без доступа: <b>{without_access}</b>\n\n"
        f"Сегмент: <b>{filter_label}</b>"
        f" · Стр. <b>{overview.current_page + 1}</b>"
        f" · В выборке: <b>{overview.total_filtered}</b>\n\n"
        f"{users_block}"
    )


def build_admin_users_search_prompt_text() -> str:
    return (
        "🔎 <b>Поиск пользователя</b>\n\n"
        "Отправьте одним сообщением:\n"
        "• Telegram ID\n"
        "• @username\n"
        "• или часть имени"
    )


def build_admin_users_search_result_text(result: AdminUserSearchResult) -> str:
    if result.users:
        users_block = "\n".join(format_admin_user_line(u) for u in result.users)
    else:
        users_block = "• Ничего не найдено"

    return (
        "🔎 <b>Результаты поиска</b>\n\n"
        f"Запрос: <code>{result.query}</code>\n\n"
        f"{users_block}"
    )
