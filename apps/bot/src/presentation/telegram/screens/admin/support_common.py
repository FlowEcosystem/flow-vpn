from src.presentation.telegram.datetime import format_datetime_msk


def format_support_reply(admin_telegram_id: int, text: str, created_at: object) -> str:
    if hasattr(created_at, "astimezone"):
        dt = format_datetime_msk(created_at)  # type: ignore[arg-type]
    else:
        dt = str(created_at)
    return f"• <code>{admin_telegram_id}</code> [{dt}]: {text}"
