import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

import structlog
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

logger = structlog.get_logger(__name__)


class UserLoggingMiddleware(BaseMiddleware):
    """Outer middleware that:
    - generates a unique request_id per update for log correlation
    - binds user_id / username to structlog context for every update
    - logs action type and duration at INFO level
    - logs unhandled exceptions at ERROR level before re-raising
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        structlog.contextvars.clear_contextvars()

        request_id = uuid.uuid4().hex[:12]
        structlog.contextvars.bind_contextvars(request_id=request_id)

        user = data.get("event_from_user")
        if user is not None:
            structlog.contextvars.bind_contextvars(
                user_id=user.id,
                username=user.username,
            )

        action = _describe_event(event)
        start = time.perf_counter()

        try:
            result = await handler(event, data)
        except Exception:
            elapsed_ms = round((time.perf_counter() - start) * 1000)
            logger.exception("update_error", action=action, elapsed_ms=elapsed_ms)
            raise
        else:
            elapsed_ms = round((time.perf_counter() - start) * 1000)
            logger.info("update_handled", action=action, elapsed_ms=elapsed_ms)
            return result
        finally:
            structlog.contextvars.clear_contextvars()


def _describe_event(event: TelegramObject) -> str:
    if isinstance(event, Message):
        if event.text and event.text.startswith("/"):
            command = event.text.split()[0]
            return f"command:{command}"
        if event.text:
            return "message:text"
        return "message:other"
    if isinstance(event, CallbackQuery):
        data = event.data or ""
        # truncate long callback data
        return f"callback:{data[:64]}"
    return type(event).__name__.lower()
