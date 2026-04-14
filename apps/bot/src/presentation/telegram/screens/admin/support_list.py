from src.application.support.dto import SupportTicketDetail, SupportTicketSummary
from src.presentation.telegram.datetime import format_datetime_msk

from .support_common import format_support_reply


def build_admin_support_tickets_text(tickets: tuple[SupportTicketSummary, ...]) -> str:
    if not tickets:
        tickets_block = "Открытых обращений нет."
    else:
        tickets_block = "\n".join(_format_support_ticket_line(t) for t in tickets)

    return (
        "🛟 <b>Support Desk</b>\n\n"
        f"Открытых обращений: <b>{len(tickets)}</b>\n\n"
        f"{tickets_block}"
    )


def build_admin_support_ticket_detail_text(detail: SupportTicketDetail) -> str:
    user_name = detail.user_first_name or (
        f"@{detail.user_username}" if detail.user_username else f"User {detail.user_telegram_id}"
    )
    created = format_datetime_msk(detail.created_at)
    status_label = "открыто ✅" if detail.status == "open" else "закрыто ⛔"

    replies_block = ""
    if detail.replies:
        replies_block = "\n\n<b>Ответы:</b>\n" + "\n".join(
            format_support_reply(r.admin_telegram_id, r.text, r.created_at) for r in detail.replies
        )

    return (
        f"🛟 <b>Тикет #{str(detail.id)[:8]}</b>\n\n"
        f"• Пользователь: <b>{user_name}</b>\n"
        f"• Telegram ID: <code>{detail.user_telegram_id}</code>\n"
        f"• Статус: <b>{status_label}</b>\n"
        f"• Создан: <b>{created}</b>\n\n"
        f"<b>Сообщение:</b>\n{detail.message}"
        f"{replies_block}"
    )


def _format_support_ticket_line(ticket: SupportTicketSummary) -> str:
    user_name = ticket.user_first_name or (
        f"@{ticket.user_username}" if ticket.user_username else f"User {ticket.user_telegram_id}"
    )
    created = format_datetime_msk(ticket.created_at)
    replies = f" · {ticket.reply_count} отв." if ticket.reply_count else ""
    short_msg = (ticket.message[:40] + "…") if len(ticket.message) > 40 else ticket.message
    return f"• <b>{user_name}</b> · {created}{replies}\n  <i>{short_msg}</i>"
