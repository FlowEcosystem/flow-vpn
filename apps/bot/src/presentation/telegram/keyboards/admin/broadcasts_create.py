# ruff: noqa: RUF001

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.presentation.telegram.callbacks import (
    ACTION_ADMIN_BROADCASTS_CONFIRM,
    BROADCAST_SEGMENT_PREFIX,
    MENU_ADMIN_BROADCASTS,
)


def build_admin_broadcast_segment_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👥 Все пользователи",
                    callback_data=f"{BROADCAST_SEGMENT_PREFIX}all",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🟢 С доступом",
                    callback_data=f"{BROADCAST_SEGMENT_PREFIX}with_access",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚪ Без доступа",
                    callback_data=f"{BROADCAST_SEGMENT_PREFIX}without_access",
                )
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=MENU_ADMIN_BROADCASTS)],
        ]
    )


def build_admin_broadcast_text_cancel_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data=MENU_ADMIN_BROADCASTS)],
        ]
    )


def build_admin_broadcast_confirm_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Запустить рассылку",
                    callback_data=ACTION_ADMIN_BROADCASTS_CONFIRM,
                )
            ],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=MENU_ADMIN_BROADCASTS)],
        ]
    )
