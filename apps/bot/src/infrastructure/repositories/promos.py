from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.promos import PromoCodeInfo
from src.infrastructure.database.models import PromoCode, PromoRedemption


class SqlAlchemyPromoCodesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active_by_code(self, code: str) -> PromoCodeInfo | None:
        stmt = select(PromoCode).where(
            PromoCode.code == code,
            PromoCode.is_active.is_(True),
            or_(PromoCode.expires_at.is_(None), PromoCode.expires_at > datetime.now(UTC)),
            or_(
                PromoCode.max_redemptions.is_(None),
                PromoCode.current_redemptions < PromoCode.max_redemptions,
            ),
        )
        result = await self._session.execute(stmt)
        promo = result.scalar_one_or_none()
        if promo is None:
            return None
        return self._map_model(promo)

    async def list_recent_active(self, limit: int) -> tuple[PromoCodeInfo, ...]:
        stmt = (
            select(PromoCode)
            .where(
                PromoCode.is_active.is_(True),
                or_(PromoCode.expires_at.is_(None), PromoCode.expires_at > datetime.now(UTC)),
            )
            .order_by(PromoCode.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return tuple(self._map_model(model) for model in result.scalars().all())

    def _map_model(self, promo: PromoCode) -> PromoCodeInfo:
        return PromoCodeInfo(
            code=promo.code,
            title=promo.title,
            description=promo.description,
            bonus_days=promo.bonus_days,
            expires_at=promo.expires_at,
        )


class SqlAlchemyPromoRedemptionsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def count_by_user_id(self, user_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(PromoRedemption)
            .where(PromoRedemption.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def exists(self, *, promo_code: str, user_id: UUID) -> bool:
        stmt = (
            select(PromoRedemption.id)
            .join(PromoCode, PromoCode.id == PromoRedemption.promo_code_id)
            .where(PromoCode.code == promo_code, PromoRedemption.user_id == user_id)
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(self, *, promo_code: str, user_id: UUID) -> None:
        promo_stmt = select(PromoCode).where(PromoCode.code == promo_code)
        promo_result = await self._session.execute(promo_stmt)
        promo = promo_result.scalar_one()
        promo.current_redemptions += 1
        self._session.add(
            PromoRedemption(
                promo_code_id=promo.id,
                user_id=user_id,
            )
        )
        await self._session.flush()
