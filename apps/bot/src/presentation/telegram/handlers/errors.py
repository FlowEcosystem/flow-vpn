import structlog
from aiogram import Bot, Router
from aiogram.types import ErrorEvent

from src.app.config import Settings

logger = structlog.get_logger(__name__)

router = Router(name="errors")


@router.errors()
async def global_error_handler(event: ErrorEvent, bot: Bot, settings: Settings) -> None:
    """Catch all unhandled exceptions, log them and optionally notify admins."""
    update = event.update
    exc = event.exception

    # Try to extract user context for the log
    user = None
    if update.message:
        user = update.message.from_user
    elif update.callback_query:
        user = update.callback_query.from_user

    logger.error(
        "unhandled_exception",
        exc_info=exc,
        update_id=update.update_id,
        user_id=user.id if user else None,
        username=user.username if user else None,
    )

    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                f"🔴 <b>Необработанная ошибка</b>\n\n"
                f"<code>{type(exc).__name__}: {exc}</code>\n\n"
                f"Update ID: <code>{update.update_id}</code>"
                + (f"\nUser: <code>{user.id}</code>" if user else ""),
            )
        except Exception:
            pass
