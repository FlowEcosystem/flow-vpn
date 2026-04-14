from src.application.support.dto import SupportTicketDetail


def build_admin_support_reply_prompt_text(detail: SupportTicketDetail) -> str:
    user_name = detail.user_first_name or (
        f"@{detail.user_username}" if detail.user_username else f"User {detail.user_telegram_id}"
    )
    return (
        f"💬 <b>Ответ на тикет #{str(detail.id)[:8]}</b>\n\n"
        f"Пользователь: <b>{user_name}</b>\n\n"
        "Введите текст ответа:"
    )
