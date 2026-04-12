from src.application.promos.dto import (
    PromoActivationResult,
    PromoActivationStatus,
    PromoOverview,
)
from src.application.promos.ports import PromosUnitOfWork
from src.application.users import UsersUnitOfWork


class GetPromoOverviewUseCase:
    def __init__(
        self,
        users_uow: UsersUnitOfWork,
        promos_uow: PromosUnitOfWork,
    ) -> None:
        self._users_uow = users_uow
        self._promos_uow = promos_uow

    async def execute(self, telegram_id: int, *, limit: int = 3) -> PromoOverview | None:
        async with self._users_uow:
            user = await self._users_uow.users.get_by_telegram_id(telegram_id)
        if user is None:
            return None

        async with self._promos_uow:
            recent_promos = await self._promos_uow.promo_codes.list_recent_active(limit)
            total_activations = await self._promos_uow.promo_redemptions.count_by_user_id(user.id)

        return PromoOverview(
            total_activations=total_activations,
            recent_promos=recent_promos,
        )


class ApplyPromoCodeUseCase:
    def __init__(
        self,
        users_uow: UsersUnitOfWork,
        promos_uow: PromosUnitOfWork,
    ) -> None:
        self._users_uow = users_uow
        self._promos_uow = promos_uow

    async def execute(self, telegram_id: int, *, code: str) -> PromoActivationResult:
        normalized_code = code.strip().upper()
        if not normalized_code:
            raise ValueError("Введите промокод текстом.")

        async with self._users_uow:
            user = await self._users_uow.users.get_by_telegram_id(telegram_id)
        if user is None:
            return PromoActivationResult(
                status=PromoActivationStatus.NOT_FOUND,
                promo=None,
                message="Профиль не найден. Отправьте /start ещё раз.",
            )

        async with self._promos_uow:
            promo = await self._promos_uow.promo_codes.get_active_by_code(normalized_code)
            if promo is None:
                return PromoActivationResult(
                    status=PromoActivationStatus.NOT_FOUND,
                    promo=None,
                    message="Такой промокод не найден или он уже неактивен.",
                )

            if await self._promos_uow.promo_redemptions.exists(
                promo_code=promo.code,
                user_id=user.id,
            ):
                return PromoActivationResult(
                    status=PromoActivationStatus.ALREADY_USED,
                    promo=promo,
                    message="Этот промокод уже активирован в вашем аккаунте.",
                )

            await self._promos_uow.promo_redemptions.create(
                promo_code=promo.code,
                user_id=user.id,
            )
            await self._promos_uow.commit()

        return PromoActivationResult(
            status=PromoActivationStatus.APPLIED,
            promo=promo,
            message="Промокод активирован ✨",
        )
