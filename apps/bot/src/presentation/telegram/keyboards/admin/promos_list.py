# ruff: noqa: RUF001

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.promos import AdminPromoDetail
from src.presentation.telegram.callbacks import (
    ACTION_ADMIN_PROMOS,
    ADMIN_PROMO_DELETE_PREFIX,
    ADMIN_PROMO_TOGGLE_PREFIX,
    ADMIN_PROMO_VIEW_PREFIX,
    MENU_ADMIN_HOME,
    MENU_ADMIN_PROMOS,
)


def build_admin_promos_list_menu(promos: tuple[AdminPromoDetail, ...]) -> InlineKeyboardMarkup:
    inline_keyboard: list[list[InlineKeyboardButton]] = []
    for promo in promos:
        status_icon = "✅" if promo.is_active else "⛔"
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{status_icon} {promo.code}",
                    callback_data=f"{ADMIN_PROMO_VIEW_PREFIX}{promo.id}",
                )
            ]
        )
    inline_keyboard.extend(
        [
            [InlineKeyboardButton(text="➕ Создать промокод", callback_data=ACTION_ADMIN_PROMOS)],
            [InlineKeyboardButton(text="⬅️ В админку", callback_data=MENU_ADMIN_HOME)],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_admin_promo_detail_menu(promo: AdminPromoDetail) -> InlineKeyboardMarkup:
    toggle_text = "⛔ Деактивировать" if promo.is_active else "✅ Активировать"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=toggle_text,
                    callback_data=f"{ADMIN_PROMO_TOGGLE_PREFIX}{promo.id}",
                ),
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"{ADMIN_PROMO_DELETE_PREFIX}{promo.id}",
                ),
            ],
            [InlineKeyboardButton(text="⬅️ К промокодам", callback_data=MENU_ADMIN_PROMOS)],
        ]
    )
