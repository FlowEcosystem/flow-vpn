# ruff: noqa: RUF001

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.presentation.telegram.callbacks import (
    ADMIN_PROMO_SCOPE_PREFIX,
    ADMIN_PROMO_TYPE_PREFIX,
    MENU_ADMIN_PROMOS,
)


def build_admin_promo_create_cancel_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data=MENU_ADMIN_PROMOS)],
        ]
    )


def build_admin_promo_type_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📅 +Дни к подписке",
                    callback_data=f"{ADMIN_PROMO_TYPE_PREFIX}bonus_days",
                ),
                InlineKeyboardButton(
                    text="♾️ Бессрочная",
                    callback_data=f"{ADMIN_PROMO_TYPE_PREFIX}infinite",
                ),
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=MENU_ADMIN_PROMOS)],
        ]
    )


def build_admin_promo_scope_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="1️⃣ Первая активная",
                    callback_data=f"{ADMIN_PROMO_SCOPE_PREFIX}one",
                ),
                InlineKeyboardButton(
                    text="📋 Все активные",
                    callback_data=f"{ADMIN_PROMO_SCOPE_PREFIX}all",
                ),
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=MENU_ADMIN_PROMOS)],
        ]
    )
