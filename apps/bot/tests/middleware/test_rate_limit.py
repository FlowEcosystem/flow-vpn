from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.presentation.telegram.middleware.rate_limit import RateLimitMiddleware

# ── Fakes ─────────────────────────────────────────────────────────────────────

class FakeRedis:
    """In-memory Redis stub: tracks counters and expire calls."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self.expire_calls: list[tuple[str, int]] = []

    async def incr(self, key: str) -> int:
        self._counters[key] = self._counters.get(key, 0) + 1
        return self._counters[key]

    async def expire(self, key: str, seconds: int) -> None:
        self.expire_calls.append((key, seconds))


class FakeSettings:
    def __init__(
        self,
        *,
        rate_limit_requests: int = 5,
        rate_limit_window_seconds: int = 60,
        admin_ids: frozenset[int] = frozenset(),
    ) -> None:
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window_seconds = rate_limit_window_seconds
        self._admin_ids = admin_ids

    def is_admin(self, user_id: int) -> bool:
        return user_id in self._admin_ids


class FakeUser:
    def __init__(self, user_id: int = 42, username: str = "tester") -> None:
        self.id = user_id
        self.username = username


def make_event() -> MagicMock:
    """Minimal TelegramObject fake — answer() is not called in happy path."""
    event = MagicMock()
    event.answer = AsyncMock()
    return event


def make_handler(*, called: list[bool]) -> Callable:
    async def handler(event: Any, data: dict) -> str:
        called.append(True)
        return "ok"
    return handler


def make_data(
    user: FakeUser | None = None,
    redis: FakeRedis | None = None,
    settings: FakeSettings | None = None,
) -> dict:
    return {
        "event_from_user": user or FakeUser(),
        "redis": redis or FakeRedis(),
        "settings": settings or FakeSettings(),
    }


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_request_under_limit_passes_through() -> None:
    middleware = RateLimitMiddleware()
    called: list[bool] = []
    handler = make_handler(called=called)
    data = make_data(settings=FakeSettings(rate_limit_requests=5))

    result = await middleware(handler, make_event(), data)

    assert called == [True]
    assert result == "ok"


@pytest.mark.asyncio
async def test_first_request_sets_expire_on_redis_key() -> None:
    middleware = RateLimitMiddleware()
    redis = FakeRedis()
    data = make_data(redis=redis, settings=FakeSettings(rate_limit_window_seconds=120))

    await middleware(make_handler(called=[]), make_event(), data)

    assert len(redis.expire_calls) == 1
    key, ttl = redis.expire_calls[0]
    assert "42" in key
    assert ttl == 120


@pytest.mark.asyncio
async def test_second_request_in_same_window_does_not_reset_ttl() -> None:
    middleware = RateLimitMiddleware()
    redis = FakeRedis()
    data = make_data(redis=redis, settings=FakeSettings(rate_limit_requests=5))

    await middleware(make_handler(called=[]), make_event(), data)
    await middleware(make_handler(called=[]), make_event(), data)

    # expire only called on first INCR (count == 1)
    assert len(redis.expire_calls) == 1


@pytest.mark.asyncio
async def test_request_over_limit_is_blocked_and_handler_not_called() -> None:
    middleware = RateLimitMiddleware()
    redis = FakeRedis()
    settings = FakeSettings(rate_limit_requests=3)
    data = make_data(redis=redis, settings=settings)

    # exhaust limit
    for _ in range(3):
        await middleware(make_handler(called=[]), make_event(), data)

    # this is the 4th — over limit
    blocked: list[bool] = []
    event = make_event()
    result = await middleware(make_handler(called=blocked), event, data)

    assert result is None
    assert blocked == []  # handler was NOT called


@pytest.mark.asyncio
async def test_admin_bypasses_rate_limit() -> None:
    middleware = RateLimitMiddleware()
    redis = FakeRedis()
    user = FakeUser(user_id=999)
    settings = FakeSettings(rate_limit_requests=0, admin_ids=frozenset({999}))
    data = make_data(user=user, redis=redis, settings=settings)
    called: list[bool] = []

    result = await middleware(make_handler(called=called), make_event(), data)

    assert result == "ok"
    assert called == [True]
    # admin bypass: redis was never touched
    assert redis._counters == {}


@pytest.mark.asyncio
async def test_no_user_in_event_passes_through() -> None:
    """Updates without a user (e.g. channel posts) are never rate-limited."""
    middleware = RateLimitMiddleware()
    data = make_data()
    data["event_from_user"] = None
    called: list[bool] = []

    result = await middleware(make_handler(called=called), make_event(), data)

    assert result == "ok"
    assert called == [True]


@pytest.mark.asyncio
async def test_each_user_has_independent_counter() -> None:
    middleware = RateLimitMiddleware()
    redis = FakeRedis()
    settings = FakeSettings(rate_limit_requests=2)

    user_a = FakeUser(user_id=1)
    user_b = FakeUser(user_id=2)

    data_a = {**make_data(), "event_from_user": user_a, "redis": redis, "settings": settings}
    data_b = {**make_data(), "event_from_user": user_b, "redis": redis, "settings": settings}

    # user_a hits limit
    for _ in range(2):
        await middleware(make_handler(called=[]), make_event(), data_a)

    blocked_a: list[bool] = []
    await middleware(make_handler(called=blocked_a), make_event(), data_a)

    # user_b is still under limit
    called_b: list[bool] = []
    result_b = await middleware(make_handler(called=called_b), make_event(), data_b)

    assert blocked_a == []   # user_a blocked
    assert called_b == [True]  # user_b passes
    assert result_b == "ok"
