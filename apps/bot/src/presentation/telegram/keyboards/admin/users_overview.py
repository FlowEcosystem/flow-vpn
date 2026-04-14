# ruff: noqa: RUF001

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.admin import AdminUsersFilter
from src.application.users import UserSummary
from src.presentation.telegram.callbacks import (
    ACTION_ADMIN_USERS_REFRESH,
    ACTION_ADMIN_USERS_SEARCH,
    ADMIN_USERS_FILTER_PREFIX,
    ADMIN_USERS_PAGE_PREFIX,
    ADMIN_USER_VIEW_PREFIX,
    MENU_ADMIN_HOME,
)

from .bulk import build_admin_users_bulk_menu
from .users_common import build_filter_label, build_user_button_label


def build_admin_users_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔎 Найти пользователя",
                    callback_data=ACTION_ADMIN_USERS_SEARCH,
                ),
                InlineKeyboardButton(
                    text="🔄 Обновить",
                    callback_data=ACTION_ADMIN_USERS_REFRESH,
                ),
            ],
            [InlineKeyboardButton(text="⬅️ Вернуться в админку", callback_data=MENU_ADMIN_HOME)],
        ]
    )


def build_admin_users_overview_menu(
    *,
    users: tuple[UserSummary, ...],
    current_page: int,
    has_next_page: bool,
    current_filter: AdminUsersFilter,
) -> InlineKeyboardMarkup:
    inline_keyboard: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text=build_filter_label(AdminUsersFilter.ALL, current_filter),
                callback_data=f"{ADMIN_USERS_FILTER_PREFIX}{AdminUsersFilter.ALL}",
            ),
            InlineKeyboardButton(
                text=build_filter_label(AdminUsersFilter.WITH_ACCESS, current_filter),
                callback_data=f"{ADMIN_USERS_FILTER_PREFIX}{AdminUsersFilter.WITH_ACCESS}",
            ),
            InlineKeyboardButton(
                text=build_filter_label(AdminUsersFilter.WITHOUT_ACCESS, current_filter),
                callback_data=f"{ADMIN_USERS_FILTER_PREFIX}{AdminUsersFilter.WITHOUT_ACCESS}",
            ),
        ]
    ]
    inline_keyboard.extend(
        build_admin_users_bulk_menu(
            current_filter=current_filter,
            current_page=current_page,
            has_users=bool(users),
        ).inline_keyboard
    )
    for user in users:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=build_user_button_label(user),
                    callback_data=f"{ADMIN_USER_VIEW_PREFIX}{user.telegram_id}",
                )
            ]
        )

    pagination_row = []
    if current_page > 0:
        pagination_row.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"{ADMIN_USERS_PAGE_PREFIX}{current_filter}:{current_page - 1}",
            )
        )
    if has_next_page:
        pagination_row.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=f"{ADMIN_USERS_PAGE_PREFIX}{current_filter}:{current_page + 1}",
            )
        )
    if pagination_row:
        inline_keyboard.append(pagination_row)

    inline_keyboard.extend(build_admin_users_menu().inline_keyboard)
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
