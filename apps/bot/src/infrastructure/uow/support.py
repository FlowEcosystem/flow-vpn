from sqlalchemy.ext.asyncio import AsyncSession

from src.application.support.ports import SupportUnitOfWork
from src.infrastructure.repositories.support import SqlAlchemySupportTicketsRepository


class SqlAlchemySupportUnitOfWork(SupportUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        tickets_repository: SqlAlchemySupportTicketsRepository,
    ) -> None:
        self._session = session
        self.tickets = tickets_repository
        self._is_committed = False

    async def __aenter__(self) -> "SqlAlchemySupportUnitOfWork":
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
