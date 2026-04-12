from sqlalchemy.ext.asyncio import AsyncSession

from src.application.promos import PromosUnitOfWork
from src.infrastructure.repositories import (
    SqlAlchemyPromoCodesRepository,
    SqlAlchemyPromoRedemptionsRepository,
)


class SqlAlchemyPromosUnitOfWork(PromosUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        promo_codes_repository: SqlAlchemyPromoCodesRepository,
        promo_redemptions_repository: SqlAlchemyPromoRedemptionsRepository,
    ) -> None:
        self._session = session
        self.promo_codes = promo_codes_repository
        self.promo_redemptions = promo_redemptions_repository
        self._is_committed = False

    async def __aenter__(self) -> "SqlAlchemyPromosUnitOfWork":
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
