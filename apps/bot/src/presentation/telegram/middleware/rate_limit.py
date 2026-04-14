from collections.abc import Awaitable, Callable
from typing import Any

import structlog
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from redis.asyncio import Redis

from src.app.config import Settings

logger = structlog.get_logger(__name__)

_RATE_LIMIT_KEY_PREFIX = "rl:"


class RateLimitMiddleware(BaseMiddleware):
    """Fixed-window rate limiter backed by Redis.

    Uses INCR + EXPIRE: the first request in a window sets the TTL,
    subsequent ones just increment. O(1) per request, no Lua needed.

    Admins bypass the limit entirely.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        redis: Redis = data["redis"]
        settings: Settings = data["settings"]

        if settings.is_admin(user.id):
            return await handler(event, data)

        key = f"{_RATE_LIMIT_KEY_PREFIX}{user.id}"
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, settings.rate_limit_window_seconds)

        if count > settings.rate_limit_requests:
            logger.warning(
                "rate_limited",
                user_id=user.id,
                username=user.username,
                count=count,
                limit=settings.rate_limit_requests,
                window_seconds=settings.rate_limit_window_seconds,
            )
            await _answer_throttled(event)
            return None

        return await handler(event, data)


async def _answer_throttled(event: TelegramObject) -> None:
    text = "⏳ Слишком много запросов. Подождите немного."
    if isinstance(event, Message):
        await event.answer(text)
    elif isinstance(event, CallbackQuery):
        await event.answer(text, show_alert=True)
