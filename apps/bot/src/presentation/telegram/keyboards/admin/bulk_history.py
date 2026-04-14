# ruff: noqa: RUF001

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.admin import AdminUsersFilter
from src.application.admin.dto import AdminBulkOperationInfo
from src.presentation.telegram.callbacks import (
    ADMIN_USERS_BULK_HISTORY_VIEW_PREFIX,
    ADMIN_USERS_PAGE_PREFIX,
)


def build_admin_users_bulk_history_menu(
    *,
    operations: tuple[AdminBulkOperationInfo, ...],
    current_filter: AdminUsersFilter,
    current_page: int,
) -> InlineKeyboardMarkup:
    inline_keyboard: list[list[InlineKeyboardButton]] = []
    for operation in operations:
        icon = {
            "pending": "🕒",
            "running": "⏳",
            "done": "✅",
            "failed": "❌",
            "cancelled": "⛔",
        }.get(operation.status, "•")
        action = {
            "issue": "Выдача",
            "disable": "Отключение",
            "delete": "Удаление",
            "rollback_issue": "Откат выдачи",
            "rollback_disable": "Откат отключения",
        }.get(operation.action, operation.action)
        label = f"{icon} {action} · {operation.processed_users}/{operation.total_users}"
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=(
                        f"{ADMIN_USERS_BULK_HISTORY_VIEW_PREFIX}"
                        f"{operation.id}:{current_filter}:{current_page}"
                    ),
                )
            ]
        )

    inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="⬅️ К списку пользователей",
                callback_data=f"{ADMIN_USERS_PAGE_PREFIX}{current_filter}:{current_page}",
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
