# ruff: noqa: RUF001

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.presentation.telegram.callbacks import (
    MENU_ACCOUNT,
    MENU_ADMIN_HOME,
    MENU_BUY,
    MENU_HOME,
    MENU_PROMO,
    MENU_REFER,
    MENU_REVIEWS,
    MENU_STATUS,
    MENU_SUPPORT,
)


def build_start_menu(*, is_admin: bool) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [
            InlineKeyboardButton(text="⚡ Подключить VPN", callback_data=MENU_BUY),
            InlineKeyboardButton(text="👤 Личный кабинет", callback_data=MENU_ACCOUNT),
        ],
        [
            InlineKeyboardButton(text="🎁 Рефералы", callback_data=MENU_REFER),
            InlineKeyboardButton(text="🏷 Промокод", callback_data=MENU_PROMO),
        ],
        [
            InlineKeyboardButton(text="📡 Статус серверов", callback_data=MENU_STATUS),
            InlineKeyboardButton(text="💬 Отзывы", callback_data=MENU_REVIEWS),
        ],
        [InlineKeyboardButton(text="🛟 Поддержка", callback_data=MENU_SUPPORT)],
    ]
    if is_admin:
        inline_keyboard.append(
            [InlineKeyboardButton(text="🛠 Админка", callback_data=MENU_ADMIN_HOME)]
        )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_section_menu(*, action_text: str, action_callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=action_text, callback_data=action_callback)],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=MENU_HOME)],
        ]
    )


def build_vpn_access_menu(*, subscription_url: str) -> InlineKeyboardMarkup:
    inline_keyboard = []
    if subscription_url.startswith(("http://", "https://")):
        inline_keyboard.append(
            [InlineKeyboardButton(text="🔗 Открыть ссылку для подключения", url=subscription_url)]
        )

    inline_keyboard.extend(
        [
            [InlineKeyboardButton(text="👤 Открыть кабинет", callback_data=MENU_ACCOUNT)],
            [InlineKeyboardButton(text="⬅️ На главную", callback_data=MENU_HOME)],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
