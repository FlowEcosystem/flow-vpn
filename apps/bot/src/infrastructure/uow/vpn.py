from sqlalchemy.ext.asyncio import AsyncSession

from src.application.vpn import VpnAccessUnitOfWork
from src.infrastructure.repositories import (
    SqlAlchemyVpnAccessEventRepository,
    SqlAlchemyVpnAccessRepository,
)


class SqlAlchemyVpnAccessUnitOfWork(VpnAccessUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        vpn_accesses_repository: SqlAlchemyVpnAccessRepository,
        vpn_access_events_repository: SqlAlchemyVpnAccessEventRepository,
    ) -> None:
        self._session = session
        self.vpn_accesses = vpn_accesses_repository
        self.vpn_access_events = vpn_access_events_repository
        self._is_committed = False

    async def __aenter__(self) -> "SqlAlchemyVpnAccessUnitOfWork":
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
