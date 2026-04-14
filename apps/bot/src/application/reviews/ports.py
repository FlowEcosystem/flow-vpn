from typing import Protocol

from src.application.reviews.dto import PublicReview, ReviewsOverview


class ReviewsRepository(Protocol):
    async def list_recent(self, limit: int) -> tuple[PublicReview, ...]: ...

    async def get_by_user_id(self, user_id: object) -> PublicReview | None: ...

    async def upsert(self, *, user_id: object, rating: int, text: str) -> None: ...

    async def get_overview(
        self,
        limit: int,
        *,
        viewer_user_id: object = None,
    ) -> ReviewsOverview: ...


class ReviewsUnitOfWork(Protocol):
    reviews: ReviewsRepository

    async def __aenter__(self) -> "ReviewsUnitOfWork": ...

    async def __aexit__(self, exc_type: object, exc: BaseException | None, tb: object) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
