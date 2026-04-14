# ruff: noqa: RUF001

import uuid

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.presentation.telegram.callbacks import ADMIN_TICKET_VIEW_PREFIX


def build_admin_support_reply_cancel_menu(ticket_id: uuid.UUID) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data=f"{ADMIN_TICKET_VIEW_PREFIX}{ticket_id}",
                )
            ],
        ]
    )
