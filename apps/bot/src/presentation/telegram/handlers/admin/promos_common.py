from uuid import UUID

from src.application.promos import AdminPromoDetail, PromoService


def parse_promo_id(callback_data: str, prefix: str) -> UUID | None:
    raw_id = callback_data.removeprefix(prefix)
    try:
        return UUID(raw_id)
    except ValueError:
        return None


async def get_admin_promo_by_id(
    promos: PromoService,
    promo_id: UUID,
) -> AdminPromoDetail | None:
    promo_list = await promos.list_admin_promos()
    return next((promo for promo in promo_list if promo.id == promo_id), None)
