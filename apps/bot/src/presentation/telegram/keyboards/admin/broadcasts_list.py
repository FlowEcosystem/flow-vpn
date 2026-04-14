# ruff: noqa: RUF001

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.broadcasts.dto import BroadcastSummary
from src.presentation.telegram.callbacks import ACTION_ADMIN_BROADCASTS, MENU_ADMIN_HOME


def build_admin_broadcasts_menu(
    broadcasts: tuple[BroadcastSummary, ...],
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Новая рассылка", callback_data=ACTION_ADMIN_BROADCASTS)],
            [InlineKeyboardButton(text="⬅️ В админку", callback_data=MENU_ADMIN_HOME)],
        ]
    )
