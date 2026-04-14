from sqlalchemy.ext.asyncio import AsyncSession

from src.application.broadcasts.ports import BroadcastsUnitOfWork
from src.infrastructure.repositories.broadcasts import SqlAlchemyBroadcastsRepository


class SqlAlchemyBroadcastsUnitOfWork(BroadcastsUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        broadcasts_repository: SqlAlchemyBroadcastsRepository,
    ) -> None:
        self._session = session
        self.broadcasts = broadcasts_repository
        self._is_committed = False

    async def __aenter__(self) -> "SqlAlchemyBroadcastsUnitOfWork":
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
