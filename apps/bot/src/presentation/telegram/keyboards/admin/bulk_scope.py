# ruff: noqa: RUF001

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.admin import AdminUsersFilter
from src.presentation.telegram.callbacks import (
    ADMIN_USERS_BULK_DELETE_CONFIRM_PREFIX,
    ADMIN_USERS_BULK_DELETE_PREFIX,
    ADMIN_USERS_BULK_DISABLE_CONFIRM_PREFIX,
    ADMIN_USERS_BULK_DISABLE_PREFIX,
    ADMIN_USERS_BULK_HISTORY_PREFIX,
    ADMIN_USERS_BULK_ISSUE_CONFIRM_PREFIX,
    ADMIN_USERS_BULK_ISSUE_PREFIX,
    ADMIN_USERS_BULK_MENU_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_DELETE_CONFIRM_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_DELETE_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_DISABLE_CONFIRM_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_DISABLE_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_ISSUE_CONFIRM_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_ISSUE_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_MENU_PREFIX,
    ADMIN_USERS_PAGE_PREFIX,
)


def build_admin_users_bulk_menu(
    *,
    current_filter: AdminUsersFilter,
    current_page: int,
    has_users: bool,
) -> InlineKeyboardMarkup:
    if not has_users:
        return InlineKeyboardMarkup(inline_keyboard=[])

    callback_suffix = f"{current_filter}:{current_page}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚙️ Действия на странице",
                    callback_data=f"{ADMIN_USERS_BULK_MENU_PREFIX}{callback_suffix}",
                ),
                InlineKeyboardButton(
                    text="🌐 Действия над всеми",
                    callback_data=f"{ADMIN_USERS_GLOBAL_BULK_MENU_PREFIX}{callback_suffix}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗂 История запусков",
                    callback_data=f"{ADMIN_USERS_BULK_HISTORY_PREFIX}{callback_suffix}",
                ),
            ],
        ]
    )


def build_admin_users_bulk_actions_menu(
    *,
    current_filter: AdminUsersFilter,
    current_page: int,
) -> InlineKeyboardMarkup:
    callback_suffix = f"{current_filter}:{current_page}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚡ Выдать новые подписки",
                    callback_data=f"{ADMIN_USERS_BULK_ISSUE_PREFIX}{callback_suffix}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⛔ Отключить активные подписки",
                    callback_data=f"{ADMIN_USERS_BULK_DISABLE_PREFIX}{callback_suffix}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить все подписки",
                    callback_data=f"{ADMIN_USERS_BULK_DELETE_PREFIX}{callback_suffix}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ К списку пользователей",
                    callback_data=f"{ADMIN_USERS_PAGE_PREFIX}{current_filter}:{current_page}",
                )
            ],
        ]
    )


def build_admin_users_global_bulk_actions_menu(
    *,
    current_filter: AdminUsersFilter,
    current_page: int,
) -> InlineKeyboardMarkup:
    callback_suffix = f"{current_filter}:{current_page}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚡ Выдать новые подписки всем",
                    callback_data=f"{ADMIN_USERS_GLOBAL_BULK_ISSUE_PREFIX}{callback_suffix}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⛔ Отключить активные у всех",
                    callback_data=f"{ADMIN_USERS_GLOBAL_BULK_DISABLE_PREFIX}{callback_suffix}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить все подписки у всех",
                    callback_data=f"{ADMIN_USERS_GLOBAL_BULK_DELETE_PREFIX}{callback_suffix}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗂 История запусков",
                    callback_data=f"{ADMIN_USERS_BULK_HISTORY_PREFIX}{callback_suffix}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ К списку пользователей",
                    callback_data=f"{ADMIN_USERS_PAGE_PREFIX}{current_filter}:{current_page}",
                )
            ],
        ]
    )


def build_admin_users_bulk_delete_confirm_menu(
    *,
    current_filter: AdminUsersFilter,
    current_page: int,
) -> InlineKeyboardMarkup:
    callback_suffix = f"{current_filter}:{current_page}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Да, удалить все подписки",
                    callback_data=f"{ADMIN_USERS_BULK_DELETE_CONFIRM_PREFIX}{callback_suffix}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Отмена",
                    callback_data=f"{ADMIN_USERS_BULK_MENU_PREFIX}{current_filter}:{current_page}",
                )
            ],
        ]
    )


def build_admin_users_global_bulk_delete_confirm_menu(
    *,
    current_filter: AdminUsersFilter,
    current_page: int,
) -> InlineKeyboardMarkup:
    callback_suffix = f"{current_filter}:{current_page}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Да, удалить все подписки у всех",
                    callback_data=f"{ADMIN_USERS_GLOBAL_BULK_DELETE_CONFIRM_PREFIX}{callback_suffix}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Отмена",
                    callback_data=f"{ADMIN_USERS_GLOBAL_BULK_MENU_PREFIX}{current_filter}:{current_page}",
                )
            ],
        ]
    )


def build_admin_users_bulk_disable_confirm_menu(
    *,
    current_filter: AdminUsersFilter,
    current_page: int,
) -> InlineKeyboardMarkup:
    callback_suffix = f"{current_filter}:{current_page}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⛔ Да, отключить активные подписки",
                    callback_data=f"{ADMIN_USERS_BULK_DISABLE_CONFIRM_PREFIX}{callback_suffix}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Отмена",
                    callback_data=f"{ADMIN_USERS_BULK_MENU_PREFIX}{current_filter}:{current_page}",
                )
            ],
        ]
    )


def build_admin_users_global_bulk_disable_confirm_menu(
    *,
    current_filter: AdminUsersFilter,
    current_page: int,
) -> InlineKeyboardMarkup:
    callback_suffix = f"{current_filter}:{current_page}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⛔ Да, отключить активные у всех",
                    callback_data=f"{ADMIN_USERS_GLOBAL_BULK_DISABLE_CONFIRM_PREFIX}{callback_suffix}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Отмена",
                    callback_data=f"{ADMIN_USERS_GLOBAL_BULK_MENU_PREFIX}{current_filter}:{current_page}",
                )
            ],
        ]
    )


def build_admin_users_bulk_issue_confirm_menu(
    *,
    current_filter: AdminUsersFilter,
    current_page: int,
) -> InlineKeyboardMarkup:
    callback_suffix = f"{current_filter}:{current_page}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚡ Да, выдать новые подписки",
                    callback_data=f"{ADMIN_USERS_BULK_ISSUE_CONFIRM_PREFIX}{callback_suffix}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Отмена",
                    callback_data=f"{ADMIN_USERS_BULK_MENU_PREFIX}{current_filter}:{current_page}",
                )
            ],
        ]
    )


def build_admin_users_global_bulk_issue_confirm_menu(
    *,
    current_filter: AdminUsersFilter,
    current_page: int,
) -> InlineKeyboardMarkup:
    callback_suffix = f"{current_filter}:{current_page}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚡ Да, выдать новые подписки всем",
                    callback_data=f"{ADMIN_USERS_GLOBAL_BULK_ISSUE_CONFIRM_PREFIX}{callback_suffix}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Отмена",
                    callback_data=f"{ADMIN_USERS_GLOBAL_BULK_MENU_PREFIX}{current_filter}:{current_page}",
                )
            ],
        ]
    )
