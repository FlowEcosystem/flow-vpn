# ruff: noqa: RUF001

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.runtime import AccessMode
from src.presentation.telegram.callbacks import (
    ACTION_ADMIN_SET_BILLING_ENABLED,
    ACTION_ADMIN_SET_FREE_ACCESS,
    ACTION_ADMIN_SET_MAX_VPN_ACCESSES,
    MENU_ADMIN_ACCESS,
    MENU_ADMIN_BILLING,
    MENU_ADMIN_BROADCASTS,
    MENU_ADMIN_HOME,
    MENU_ADMIN_PROMOS,
    MENU_ADMIN_SUPPORT,
    MENU_ADMIN_USERS,
    MENU_HOME,
)


def build_admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎛 Режим работы", callback_data=MENU_ADMIN_ACCESS),
                InlineKeyboardButton(text="💳 Биллинг", callback_data=MENU_ADMIN_BILLING),
            ],
            [
                InlineKeyboardButton(text="👥 Пользователи", callback_data=MENU_ADMIN_USERS),
                InlineKeyboardButton(text="🎁 Промокоды", callback_data=MENU_ADMIN_PROMOS),
            ],
            [
                InlineKeyboardButton(text="📢 Рассылки", callback_data=MENU_ADMIN_BROADCASTS),
                InlineKeyboardButton(text="🛟 Support Desk", callback_data=MENU_ADMIN_SUPPORT),
            ],
            [
                InlineKeyboardButton(text="⬅️ Вернуться в клиентское меню", callback_data=MENU_HOME),
            ],
        ]
    )


def build_admin_section_menu(*, action_text: str, action_callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=action_text, callback_data=action_callback)],
            [InlineKeyboardButton(text="⬅️ Вернуться в админку", callback_data=MENU_ADMIN_HOME)],
        ]
    )


def build_access_mode_menu(*, current_mode: AccessMode) -> InlineKeyboardMarkup:
    free_label = (
        "🟢 Бесплатная выдача"
        if current_mode is AccessMode.FREE_ACCESS
        else "⚪ Бесплатная выдача"
    )
    billing_label = (
        "🟢 Биллинг активен"
        if current_mode is AccessMode.BILLING_ENABLED
        else "⚪ Биллинг активен"
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=free_label, callback_data=ACTION_ADMIN_SET_FREE_ACCESS)],
            [
                InlineKeyboardButton(
                    text=billing_label,
                    callback_data=ACTION_ADMIN_SET_BILLING_ENABLED,
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔢 Лимит подписок на пользователя",
                    callback_data=ACTION_ADMIN_SET_MAX_VPN_ACCESSES,
                )
            ],
            [InlineKeyboardButton(text="⬅️ Вернуться в админку", callback_data=MENU_ADMIN_HOME)],
        ]
    )
