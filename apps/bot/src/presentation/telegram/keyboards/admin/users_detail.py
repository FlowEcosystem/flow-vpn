# ruff: noqa: RUF001

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.admin.dto import AdminUserDetail
from src.presentation.telegram.callbacks import (
    ADMIN_ACCESS_DELETE_PREFIX,
    ADMIN_ACCESS_DISABLE_PREFIX,
    ADMIN_ACCESS_ENABLE_PREFIX,
    ADMIN_ACCESS_REISSUE_PREFIX,
    ADMIN_USER_HISTORY_PREFIX,
    ADMIN_USER_ISSUE_PREFIX,
    ADMIN_USER_VIEW_PREFIX,
    MENU_ADMIN_USERS,
)


def build_admin_user_detail_menu(detail: AdminUserDetail) -> InlineKeyboardMarkup:
    telegram_id = detail.user.telegram_id
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text="⚡ Выдать новую подписку",
                callback_data=f"{ADMIN_USER_ISSUE_PREFIX}{telegram_id}",
            )
        ]
    ]

    for number, access in enumerate(detail.vpn_accesses, start=1):
        action_row = []
        if access.status == "active":
            action_row.append(
                InlineKeyboardButton(
                    text=f"♻️ Перевыпустить #{number}",
                    callback_data=f"{ADMIN_ACCESS_REISSUE_PREFIX}{access.id}",
                )
            )
            action_row.append(
                InlineKeyboardButton(
                    text=f"⛔ Отключить #{number}",
                    callback_data=f"{ADMIN_ACCESS_DISABLE_PREFIX}{access.id}",
                )
            )
        else:
            action_row.append(
                InlineKeyboardButton(
                    text=f"✅ Включить #{number}",
                    callback_data=f"{ADMIN_ACCESS_ENABLE_PREFIX}{access.id}",
                )
            )
        action_row.append(
            InlineKeyboardButton(
                text=f"🗑 Удалить #{number}",
                callback_data=f"{ADMIN_ACCESS_DELETE_PREFIX}{access.id}",
            )
        )

        url_row = []
        if access.subscription_url.startswith(("http://", "https://")):
            url_row.append(
                InlineKeyboardButton(
                    text=f"🔗 Открыть подписку #{number}",
                    url=access.subscription_url,
                )
            )
        if url_row:
            inline_keyboard.append(url_row)
        inline_keyboard.append(action_row)

    inline_keyboard.extend(
        [
            [
                InlineKeyboardButton(
                    text="🕓 История доступа",
                    callback_data=f"{ADMIN_USER_HISTORY_PREFIX}{telegram_id}",
                )
            ],
            [InlineKeyboardButton(text="⬅️ К пользователям", callback_data=MENU_ADMIN_USERS)],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_admin_user_access_menu(
    *,
    subscription_url: str,
    telegram_id: int,
) -> InlineKeyboardMarkup:
    inline_keyboard = []
    if subscription_url.startswith(("http://", "https://")):
        inline_keyboard.append(
            [InlineKeyboardButton(text="🔗 Открыть подписку", url=subscription_url)]
        )
    inline_keyboard.extend(
        [
            [
                InlineKeyboardButton(
                    text="⬅️ В карточку пользователя",
                    callback_data=f"{ADMIN_USER_VIEW_PREFIX}{telegram_id}",
                )
            ],
            [InlineKeyboardButton(text="⬅️ К пользователям", callback_data=MENU_ADMIN_USERS)],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
