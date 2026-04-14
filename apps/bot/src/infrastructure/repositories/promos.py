import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.promos import PromoCodeInfo
from src.application.promos.dto import AdminPromoDetail, NewPromoCodeData
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
                or_(
                    PromoCode.max_redemptions.is_(None),
                    PromoCode.current_redemptions < PromoCode.max_redemptions,
                ),
            )
            .order_by(PromoCode.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return tuple(self._map_model(model) for model in result.scalars().all())

    async def list_all(self, limit: int = 30) -> tuple[AdminPromoDetail, ...]:
        stmt = select(PromoCode).order_by(PromoCode.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return tuple(self._map_admin_model(model) for model in result.scalars().all())

    async def get_by_id(self, promo_id: UUID) -> AdminPromoDetail | None:
        stmt = select(PromoCode).where(PromoCode.id == promo_id)
        result = await self._session.execute(stmt)
        promo = result.scalar_one_or_none()
        if promo is None:
            return None
        return self._map_admin_model(promo)

    async def create(self, data: NewPromoCodeData) -> AdminPromoDetail:
        promo = PromoCode(
            id=uuid.uuid4(),
            code=data.code.upper(),
            title=data.title,
            bonus_days=data.bonus_days,
            is_infinite=data.is_infinite,
            apply_to_all=data.apply_to_all,
            max_redemptions=data.max_redemptions,
            is_active=True,
            current_redemptions=0,
        )
        self._session.add(promo)
        await self._session.flush()
        await self._session.refresh(promo)
        return self._map_admin_model(promo)

    async def set_active(self, promo_id: UUID, *, is_active: bool) -> None:
        stmt = select(PromoCode).where(PromoCode.id == promo_id)
        result = await self._session.execute(stmt)
        promo = result.scalar_one_or_none()
        if promo is None:
            return
        promo.is_active = is_active
        await self._session.flush()

    async def delete(self, promo_id: UUID) -> None:
        stmt = select(PromoCode).where(PromoCode.id == promo_id)
        result = await self._session.execute(stmt)
        promo = result.scalar_one_or_none()
        if promo is None:
            return
        await self._session.delete(promo)
        await self._session.flush()

    def _map_model(self, promo: PromoCode) -> PromoCodeInfo:
        if promo.max_redemptions is not None:
            remaining = max(0, promo.max_redemptions - promo.current_redemptions)
        else:
            remaining = None
        return PromoCodeInfo(
            code=promo.code,
            title=promo.title,
            description=promo.description,
            bonus_days=promo.bonus_days,
            is_infinite=promo.is_infinite,
            apply_to_all=promo.apply_to_all,
            expires_at=promo.expires_at,
            remaining_activations=remaining,
        )

    def _map_admin_model(self, promo: PromoCode) -> AdminPromoDetail:
        return AdminPromoDetail(
            id=promo.id,
            code=promo.code,
            title=promo.title,
            bonus_days=promo.bonus_days,
            is_infinite=promo.is_infinite,
            apply_to_all=promo.apply_to_all,
            is_active=promo.is_active,
            max_redemptions=promo.max_redemptions,
            current_redemptions=promo.current_redemptions,
            expires_at=promo.expires_at,
            created_at=promo.created_at,
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
