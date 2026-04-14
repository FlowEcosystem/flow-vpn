# ruff: noqa: RUF001

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.support.dto import SupportTicketDetail, SupportTicketSummary
from src.presentation.telegram.callbacks import (
    ADMIN_TICKET_CLOSE_PREFIX,
    ADMIN_TICKET_REPLY_PREFIX,
    ADMIN_TICKET_VIEW_PREFIX,
    MENU_ADMIN_HOME,
    MENU_ADMIN_SUPPORT,
)


def build_admin_support_tickets_menu(
    tickets: tuple[SupportTicketSummary, ...],
) -> InlineKeyboardMarkup:
    inline_keyboard: list[list[InlineKeyboardButton]] = []
    for ticket in tickets:
        user_label = ticket.user_first_name or (
            f"@{ticket.user_username}" if ticket.user_username else str(ticket.user_telegram_id)
        )
        replies_suffix = f" [{ticket.reply_count}]" if ticket.reply_count else ""
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"#{str(ticket.id)[:6]} · {user_label[:20]}{replies_suffix}",
                    callback_data=f"{ADMIN_TICKET_VIEW_PREFIX}{ticket.id}",
                )
            ]
        )
    inline_keyboard.append(
        [InlineKeyboardButton(text="⬅️ В админку", callback_data=MENU_ADMIN_HOME)]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_admin_support_ticket_detail_menu(detail: SupportTicketDetail) -> InlineKeyboardMarkup:
    ticket_id = str(detail.id)
    inline_keyboard: list[list[InlineKeyboardButton]] = []
    if detail.status == "open":
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="💬 Ответить",
                    callback_data=f"{ADMIN_TICKET_REPLY_PREFIX}{ticket_id}",
                ),
                InlineKeyboardButton(
                    text="✅ Закрыть тикет",
                    callback_data=f"{ADMIN_TICKET_CLOSE_PREFIX}{ticket_id}",
                ),
            ]
        )
    inline_keyboard.extend(
        [
            [InlineKeyboardButton(text="⬅️ К тикетам", callback_data=MENU_ADMIN_SUPPORT)],
            [InlineKeyboardButton(text="⬅️ В админку", callback_data=MENU_ADMIN_HOME)],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
