
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.vpn import VpnAccess
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
    USER_ACCESS_DELETE_PREFIX,
    USER_ACCESS_DISABLE_PREFIX,
    USER_ACCESS_ENABLE_PREFIX,
    USER_ACCESS_VIEW_PREFIX,
)
from src.presentation.telegram.datetime import format_datetime_msk


def build_start_menu(*, is_admin: bool) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [
            InlineKeyboardButton(text="👤 Кабинет", callback_data=MENU_ACCOUNT),
        ],
        [
            InlineKeyboardButton(text="🎁 Рефералы", callback_data=MENU_REFER),
            InlineKeyboardButton(text="🏷 Промокод", callback_data=MENU_PROMO),
        ],
        [
            InlineKeyboardButton(text="📡 Статус", callback_data=MENU_STATUS),
            InlineKeyboardButton(text="💬 Отзывы", callback_data=MENU_REVIEWS),
            InlineKeyboardButton(text="🛟 Поддержка", callback_data=MENU_SUPPORT),
        ],
    ]
    if is_admin:
        inline_keyboard.append(
            [InlineKeyboardButton(text="🛠 Панель управления", callback_data=MENU_ADMIN_HOME)]
        )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_section_menu(*, action_text: str, action_callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=action_text, callback_data=action_callback)],
            [InlineKeyboardButton(text="🏠 Главная", callback_data=MENU_HOME)],
        ]
    )


def build_vpn_access_menu(*, subscription_url: str) -> InlineKeyboardMarkup:
    inline_keyboard = []
    if subscription_url.startswith(("http://", "https://")):
        inline_keyboard.append(
            [InlineKeyboardButton(text="🔗 Подключиться", url=subscription_url)]
        )

    inline_keyboard.extend(
        [
            [
                InlineKeyboardButton(text="👤 Кабинет", callback_data=MENU_ACCOUNT),
                InlineKeyboardButton(text="🏠 Главная", callback_data=MENU_HOME),
            ],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_subscriptions_list_menu(
    accesses: tuple[VpnAccess, ...],
) -> InlineKeyboardMarkup:
    inline_keyboard: list[list[InlineKeyboardButton]] = []
    for i, access in enumerate(accesses, 1):
        status_icon = "🟢" if access.status == "active" else "🔴"
        expires = (
            format_datetime_msk(access.expires_at, include_tz=False)
            if access.expires_at is not None
            else "бессрочно"
        )
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{status_icon} Подписка #{i}  ·  до {expires}",
                    callback_data=f"{USER_ACCESS_VIEW_PREFIX}{access.id}",
                )
            ]
        )

    inline_keyboard.append(
        [
            InlineKeyboardButton(text="➕ Добавить", callback_data=MENU_BUY),
            InlineKeyboardButton(text="🏠 Главная", callback_data=MENU_HOME),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_subscription_detail_menu(
    access: VpnAccess,
) -> InlineKeyboardMarkup:
    inline_keyboard: list[list[InlineKeyboardButton]] = []

    if access.subscription_url.startswith(("http://", "https://")):
        inline_keyboard.append(
            [InlineKeyboardButton(text="🔗 Подключиться", url=access.subscription_url)]
        )

    if access.status == "active":
        inline_keyboard.append([
            InlineKeyboardButton(
                text="🚫 Отключить",
                callback_data=f"{USER_ACCESS_DISABLE_PREFIX}{access.id}",
            ),
            InlineKeyboardButton(
                text="🗑 Удалить",
                callback_data=f"{USER_ACCESS_DELETE_PREFIX}{access.id}",
            ),
        ])
    else:
        inline_keyboard.append([
            InlineKeyboardButton(
                text="▶️ Возобновить",
                callback_data=f"{USER_ACCESS_ENABLE_PREFIX}{access.id}",
            ),
            InlineKeyboardButton(
                text="🗑 Удалить",
                callback_data=f"{USER_ACCESS_DELETE_PREFIX}{access.id}",
            ),
        ])

    inline_keyboard.append(
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=MENU_ACCOUNT),
            InlineKeyboardButton(text="🏠 Главная", callback_data=MENU_HOME),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
