# ruff: noqa: RUF001

import uuid

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.admin import AdminUsersFilter
from src.presentation.telegram.callbacks import (
    ADMIN_USERS_BULK_HISTORY_PREFIX,
    ADMIN_USERS_BULK_HISTORY_VIEW_PREFIX,
    ADMIN_USERS_BULK_OPERATION_CANCEL_PREFIX,
    ADMIN_USERS_BULK_OPERATION_REFRESH_PREFIX,
    ADMIN_USERS_BULK_OPERATION_ROLLBACK_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_MENU_PREFIX,
    ADMIN_USERS_BULK_MENU_PREFIX,
    ADMIN_USERS_PAGE_PREFIX,
)


def build_admin_users_bulk_progress_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[])


def build_admin_users_bulk_result_menu(
    *,
    current_filter: AdminUsersFilter,
    current_page: int,
    global_scope: bool,
) -> InlineKeyboardMarkup:
    menu_prefix = (
        ADMIN_USERS_GLOBAL_BULK_MENU_PREFIX if global_scope else ADMIN_USERS_BULK_MENU_PREFIX
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ К массовым действиям",
                    callback_data=f"{menu_prefix}{current_filter}:{current_page}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👥 К списку пользователей",
                    callback_data=f"{ADMIN_USERS_PAGE_PREFIX}{current_filter}:{current_page}",
                ),
            ],
        ]
    )


def build_admin_users_bulk_operation_status_menu(
    *,
    operation_id: uuid.UUID,
    current_filter: AdminUsersFilter,
    current_page: int,
    global_scope: bool,
    can_cancel: bool = False,
    can_rollback: bool = False,
) -> InlineKeyboardMarkup:
    menu_prefix = (
        ADMIN_USERS_GLOBAL_BULK_MENU_PREFIX if global_scope else ADMIN_USERS_BULK_MENU_PREFIX
    )
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text="🔄 Обновить статус",
                callback_data=f"{ADMIN_USERS_BULK_OPERATION_REFRESH_PREFIX}{operation_id}",
            ),
        ]
    ]
    if can_cancel:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="⛔ Отменить операцию",
                    callback_data=f"{ADMIN_USERS_BULK_OPERATION_CANCEL_PREFIX}{operation_id}",
                ),
            ]
        )
    if can_rollback:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="↩️ Откатить операцию",
                    callback_data=(
                        f"{ADMIN_USERS_BULK_OPERATION_ROLLBACK_PREFIX}"
                        f"{operation_id}:{current_filter}:{current_page}"
                    ),
                ),
            ]
        )
    inline_keyboard.extend(
        [
            [
                InlineKeyboardButton(
                    text="⬅️ К массовым действиям",
                    callback_data=f"{menu_prefix}{current_filter}:{current_page}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👥 К списку пользователей",
                    callback_data=f"{ADMIN_USERS_PAGE_PREFIX}{current_filter}:{current_page}",
                ),
            ],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_admin_users_bulk_history_detail_menu(
    *,
    operation_id: uuid.UUID,
    current_filter: AdminUsersFilter,
    current_page: int,
    can_cancel: bool = False,
    can_rollback: bool = False,
) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text="🔄 Обновить статус",
                callback_data=(
                    f"{ADMIN_USERS_BULK_HISTORY_VIEW_PREFIX}"
                    f"{operation_id}:{current_filter}:{current_page}"
                ),
            ),
        ]
    ]
    if can_cancel:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="⛔ Отменить операцию",
                    callback_data=f"{ADMIN_USERS_BULK_OPERATION_CANCEL_PREFIX}{operation_id}",
                ),
            ]
        )
    if can_rollback:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="↩️ Откатить операцию",
                    callback_data=(
                        f"{ADMIN_USERS_BULK_OPERATION_ROLLBACK_PREFIX}"
                        f"{operation_id}:{current_filter}:{current_page}"
                    ),
                ),
            ]
        )
    inline_keyboard.extend(
        [
            [
                InlineKeyboardButton(
                    text="⬅️ К истории запусков",
                    callback_data=f"{ADMIN_USERS_BULK_HISTORY_PREFIX}{current_filter}:{current_page}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👥 К списку пользователей",
                    callback_data=f"{ADMIN_USERS_PAGE_PREFIX}{current_filter}:{current_page}",
                ),
            ],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
