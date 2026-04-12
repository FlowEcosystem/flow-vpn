from sqlalchemy.ext.asyncio import AsyncSession

from src.application.reviews import ReviewsUnitOfWork
from src.infrastructure.repositories import SqlAlchemyReviewsRepository


class SqlAlchemyReviewsUnitOfWork(ReviewsUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        reviews_repository: SqlAlchemyReviewsRepository,
    ) -> None:
        self._session = session
        self.reviews = reviews_repository
        self._is_committed = False

    async def __aenter__(self) -> "SqlAlchemyReviewsUnitOfWork":
        self._is_committed = False
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc: BaseException | None,
        tb: object,
    ) -> None:
        if exc is not None or not self._is_committed:
            await self.rollback()

    async def commit(self) -> None:
        await self._session.commit()
        self._is_committed = True

    async def rollback(self) -> None:
        await self._session.rollback()
