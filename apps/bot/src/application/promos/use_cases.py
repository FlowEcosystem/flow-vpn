from uuid import UUID

from src.application.promos.admin import (
    create_admin_promo,
    delete_admin_promo,
    list_admin_promos,
    toggle_admin_promo,
)
from src.application.promos.dto import (
    AdminPromoDetail,
    NewPromoCodeData,
    PromoActivationResult,
    PromoEligibility,
    PromoOverview,
)
from src.application.promos.ports import PromosUnitOfWork
from src.application.promos.public import apply_promo, check_promo_eligibility, get_promo_overview
from src.application.users import UsersUnitOfWork
from src.application.vpn.ports import VpnAccessUnitOfWork, VpnProvisioningGateway


class PromoService:
    def __init__(
        self,
        users_uow: UsersUnitOfWork,
        promos_uow: PromosUnitOfWork,
        vpn_access_uow: VpnAccessUnitOfWork,
        provisioning_gateway: VpnProvisioningGateway,
    ) -> None:
        self._users_uow = users_uow
        self._promos_uow = promos_uow
        self._vpn_access_uow = vpn_access_uow
        self._provisioning_gateway = provisioning_gateway

    async def get_overview(self, telegram_id: int, *, limit: int = 5) -> PromoOverview | None:
        return await get_promo_overview(
            users_uow=self._users_uow,
            promos_uow=self._promos_uow,
            telegram_id=telegram_id,
            limit=limit,
        )

    async def check_eligibility(self, telegram_id: int, *, code: str) -> PromoEligibility:
        return await check_promo_eligibility(
            users_uow=self._users_uow,
            promos_uow=self._promos_uow,
            vpn_access_uow=self._vpn_access_uow,
            telegram_id=telegram_id,
            code=code,
        )

    async def apply(
        self,
        telegram_id: int,
        *,
        code: str,
        target_access_id: UUID | None = None,
    ) -> PromoActivationResult:
        return await apply_promo(
            users_uow=self._users_uow,
            promos_uow=self._promos_uow,
            vpn_access_uow=self._vpn_access_uow,
            provisioning_gateway=self._provisioning_gateway,
            telegram_id=telegram_id,
            code=code,
            target_access_id=target_access_id,
        )

    async def list_admin_promos(self, *, limit: int = 30) -> tuple[AdminPromoDetail, ...]:
        return await list_admin_promos(promos_uow=self._promos_uow, limit=limit)

    async def create_promo(self, data: NewPromoCodeData) -> AdminPromoDetail:
        return await create_admin_promo(promos_uow=self._promos_uow, data=data)

    async def toggle_promo(self, promo_id: UUID, *, is_active: bool) -> AdminPromoDetail | None:
        return await toggle_admin_promo(
            promos_uow=self._promos_uow,
            promo_id=promo_id,
            is_active=is_active,
        )

    async def delete_promo(self, promo_id: UUID) -> bool:
        return await delete_admin_promo(promos_uow=self._promos_uow, promo_id=promo_id)
