from uuid import UUID

import structlog

from src.application.promos.dto import AdminPromoDetail, NewPromoCodeData
from src.application.promos.ports import PromosUnitOfWork

logger = structlog.get_logger(__name__)


async def list_admin_promos(
    *,
    promos_uow: PromosUnitOfWork,
    limit: int = 30,
) -> tuple[AdminPromoDetail, ...]:
    async with promos_uow:
        return await promos_uow.promo_codes.list_all(limit)


async def create_admin_promo(
    *,
    promos_uow: PromosUnitOfWork,
    data: NewPromoCodeData,
) -> AdminPromoDetail:
    async with promos_uow:
        promo = await promos_uow.promo_codes.create(data)
        await promos_uow.commit()
    logger.info(
        "promo_created",
        code=promo.code,
        bonus_days=promo.bonus_days,
        promo_id=str(promo.id),
    )
    return promo


async def toggle_admin_promo(
    *,
    promos_uow: PromosUnitOfWork,
    promo_id: UUID,
    is_active: bool,
) -> AdminPromoDetail | None:
    async with promos_uow:
        await promos_uow.promo_codes.set_active(promo_id, is_active=is_active)
        await promos_uow.commit()
        result = await promos_uow.promo_codes.get_by_id(promo_id)
    logger.info("promo_toggled", promo_id=str(promo_id), is_active=is_active)
    return result


async def delete_admin_promo(
    *,
    promos_uow: PromosUnitOfWork,
    promo_id: UUID,
) -> bool:
    async with promos_uow:
        promo = await promos_uow.promo_codes.get_by_id(promo_id)
        if promo is None:
            return False
        await promos_uow.promo_codes.delete(promo_id)
        await promos_uow.commit()
    logger.info("promo_deleted", promo_id=str(promo_id))
    return True
