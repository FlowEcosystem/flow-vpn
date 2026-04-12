from sqlalchemy.ext.asyncio import AsyncSession

from src.application.users import UsersUnitOfWork
from src.infrastructure.repositories import SqlAlchemyUsersRepository


class SqlAlchemyUsersUnitOfWork(UsersUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        users_repository: SqlAlchemyUsersRepository,
    ) -> None:
        self._session = session
        self.users = users_repository
        self._is_committed = False

    async def __aenter__(self) -> "SqlAlchemyUsersUnitOfWork":
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
