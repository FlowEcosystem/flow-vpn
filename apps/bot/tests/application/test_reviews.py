from uuid import UUID

import pytest

from src.application.reviews.use_cases import ReviewsService
from tests.conftest import FakeUsersUnitOfWork, build_user

# ── Fakes ─────────────────────────────────────────────────────────────────────

class FakeReviewsRepository:
    def __init__(self) -> None:
        self.upserted: list[dict] = []

    async def upsert(self, *, user_id: UUID, rating: int, text: str) -> None:
        self.upserted.append({"user_id": user_id, "rating": rating, "text": text})

    async def get_overview(self, limit: int, *, viewer_user_id: UUID | None):
        raise NotImplementedError


class FakeReviewsUnitOfWork:
    def __init__(self) -> None:
        self.reviews = FakeReviewsRepository()
        self.commit_count = 0

    async def __aenter__(self) -> "FakeReviewsUnitOfWork":
        return self

    async def __aexit__(self, *_) -> None:
        pass

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        pass


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_review_upserts_and_commits() -> None:
    user = build_user()
    users_uow = FakeUsersUnitOfWork(user)
    reviews_uow = FakeReviewsUnitOfWork()
    service = ReviewsService(users_uow, reviews_uow)

    result = await service.create(user.telegram_id, rating=5, text="Great service!")

    assert result is True
    assert reviews_uow.reviews.upserted == [
        {"user_id": user.id, "rating": 5, "text": "Great service!"}
    ]
    assert reviews_uow.commit_count == 1


@pytest.mark.asyncio
async def test_create_review_strips_whitespace_from_text() -> None:
    user = build_user()
    users_uow = FakeUsersUnitOfWork(user)
    reviews_uow = FakeReviewsUnitOfWork()
    service = ReviewsService(users_uow, reviews_uow)

    await service.create(user.telegram_id, rating=4, text="  nice  ")

    assert reviews_uow.reviews.upserted[0]["text"] == "nice"


@pytest.mark.asyncio
async def test_create_review_allows_empty_text() -> None:
    user = build_user()
    users_uow = FakeUsersUnitOfWork(user)
    reviews_uow = FakeReviewsUnitOfWork()
    service = ReviewsService(users_uow, reviews_uow)

    result = await service.create(user.telegram_id, rating=3, text="")

    assert result is True
    assert reviews_uow.reviews.upserted[0]["text"] == ""


@pytest.mark.asyncio
async def test_create_review_too_short_text_raises_value_error() -> None:
    user = build_user()
    users_uow = FakeUsersUnitOfWork(user)
    reviews_uow = FakeReviewsUnitOfWork()
    service = ReviewsService(users_uow, reviews_uow)

    with pytest.raises(ValueError):
        await service.create(user.telegram_id, rating=3, text="ok")


@pytest.mark.asyncio
async def test_create_review_invalid_rating_raises_value_error() -> None:
    user = build_user()
    users_uow = FakeUsersUnitOfWork(user)
    reviews_uow = FakeReviewsUnitOfWork()
    service = ReviewsService(users_uow, reviews_uow)

    with pytest.raises(ValueError):
        await service.create(user.telegram_id, rating=6, text="")


@pytest.mark.asyncio
async def test_create_review_unknown_user_returns_false() -> None:
    users_uow = FakeUsersUnitOfWork(user=None)
    reviews_uow = FakeReviewsUnitOfWork()
    service = ReviewsService(users_uow, reviews_uow)

    result = await service.create(9999, rating=5, text="")

    assert result is False
    assert reviews_uow.reviews.upserted == []
    assert reviews_uow.commit_count == 0
