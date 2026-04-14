from uuid import UUID

import structlog

from src.application.promos.common import get_eligible_accesses, number_eligible_accesses, promo_has_effect
from src.application.promos.dto import (
    PromoActivationResult,
    PromoActivationStatus,
    PromoEligibility,
    PromoOverview,
)
from src.application.promos.ports import PromosUnitOfWork
from src.application.users import UsersUnitOfWork
from src.application.vpn.dto import UpdateVpnAccessData, VpnAccess
from src.application.vpn.ports import VpnAccessUnitOfWork, VpnProvisioningGateway

logger = structlog.get_logger(__name__)


async def get_promo_overview(
    *,
    users_uow: UsersUnitOfWork,
    promos_uow: PromosUnitOfWork,
    telegram_id: int,
    limit: int = 5,
) -> PromoOverview | None:
    async with users_uow:
        user = await users_uow.users.get_by_telegram_id(telegram_id)
    if user is None:
        return None

    async with promos_uow:
        recent_promos = await promos_uow.promo_codes.list_recent_active(limit)
        total_activations = await promos_uow.promo_redemptions.count_by_user_id(user.id)

    return PromoOverview(
        total_activations=total_activations,
        recent_promos=recent_promos,
    )


async def check_promo_eligibility(
    *,
    users_uow: UsersUnitOfWork,
    promos_uow: PromosUnitOfWork,
    vpn_access_uow: VpnAccessUnitOfWork,
    telegram_id: int,
    code: str,
) -> PromoEligibility:
    normalized = code.strip().upper()

    async with users_uow:
        user = await users_uow.users.get_by_telegram_id(telegram_id)
    if user is None:
        return PromoEligibility(promo=None, already_used=False, eligible_accesses=())

    async with promos_uow:
        promo = await promos_uow.promo_codes.get_active_by_code(normalized)
        if promo is None:
            return PromoEligibility(promo=None, already_used=False, eligible_accesses=())

        already_used = await promos_uow.promo_redemptions.exists(
            promo_code=promo.code,
            user_id=user.id,
        )

    if not promo_has_effect(promo):
        return PromoEligibility(promo=promo, already_used=already_used, eligible_accesses=())

    async with vpn_access_uow:
        all_accesses = list(await vpn_access_uow.vpn_accesses.list_by_user_id(user.id))

    eligible = get_eligible_accesses(all_accesses)
    numbered = number_eligible_accesses(all_accesses, eligible)
    return PromoEligibility(promo=promo, already_used=already_used, eligible_accesses=numbered)


async def apply_promo_to_targets(
    *,
    vpn_access_uow: VpnAccessUnitOfWork,
    provisioning_gateway: VpnProvisioningGateway,
    targets: list[VpnAccess],
    promo,
) -> None:
    for access in targets:
        try:
            if promo.is_infinite:
                provisioned = await provisioning_gateway.make_vless_access_infinite(
                    access.external_username
                )
            else:
                provisioned = await provisioning_gateway.extend_vless_access(
                    access.external_username, promo.bonus_days
                )
            async with vpn_access_uow as uow:
                await uow.vpn_accesses.update(
                    access.id,
                    UpdateVpnAccessData(
                        status=provisioned.status,
                        subscription_url=provisioned.subscription_url,
                        vless_links=provisioned.vless_links,
                        issued_at=provisioned.issued_at,
                        expires_at=provisioned.expires_at,
                    ),
                )
                await uow.commit()
        except Exception:
            logger.exception(
                "promo_apply_failed",
                access_id=str(access.id),
                is_infinite=promo.is_infinite,
                bonus_days=promo.bonus_days,
            )


async def apply_promo(
    *,
    users_uow: UsersUnitOfWork,
    promos_uow: PromosUnitOfWork,
    vpn_access_uow: VpnAccessUnitOfWork,
    provisioning_gateway: VpnProvisioningGateway,
    telegram_id: int,
    code: str,
    target_access_id: UUID | None = None,
) -> PromoActivationResult:
    normalized_code = code.strip().upper()
    if not normalized_code:
        raise ValueError("Введите промокод текстом.")

    async with users_uow:
        user = await users_uow.users.get_by_telegram_id(telegram_id)
    if user is None:
        return PromoActivationResult(
            status=PromoActivationStatus.NOT_FOUND,
            promo=None,
            message="Профиль не найден. Отправьте /start ещё раз.",
        )

    async with promos_uow:
        promo = await promos_uow.promo_codes.get_active_by_code(normalized_code)
        if promo is None:
            logger.info("promo_not_found", telegram_id=telegram_id, code=normalized_code)
            return PromoActivationResult(
                status=PromoActivationStatus.NOT_FOUND,
                promo=None,
                message="Такой промокод не найден или он уже неактивен.",
            )

        if await promos_uow.promo_redemptions.exists(
            promo_code=promo.code,
            user_id=user.id,
        ):
            logger.info("promo_already_used", telegram_id=telegram_id, code=normalized_code)
            return PromoActivationResult(
                status=PromoActivationStatus.ALREADY_USED,
                promo=promo,
                message="Этот промокод уже активирован в вашем аккаунте.",
            )

    has_effect = promo_has_effect(promo)
    targets: list[VpnAccess] = []

    if has_effect:
        async with vpn_access_uow:
            all_accesses = list(await vpn_access_uow.vpn_accesses.list_by_user_id(user.id))
        eligible = get_eligible_accesses(all_accesses)

        if promo.apply_to_all:
            targets = eligible
        elif target_access_id is not None:
            targets = [a for a in eligible if a.id == target_access_id]
            if not targets:
                return PromoActivationResult(
                    status=PromoActivationStatus.NO_ELIGIBLE_ACCESSES,
                    promo=promo,
                    message=(
                        "Выбранная подписка не подходит для этого промокода "
                        "(возможно, она уже бессрочная или неактивна)."
                    ),
                )
        elif len(eligible) == 1:
            targets = eligible
        else:
            return PromoActivationResult(
                status=PromoActivationStatus.NO_ELIGIBLE_ACCESSES,
                promo=promo,
                message="Нужно выбрать подписку для применения промокода.",
            )

        if not targets:
            return PromoActivationResult(
                status=PromoActivationStatus.NO_ELIGIBLE_ACCESSES,
                promo=promo,
                message=(
                    "Нет подходящих подписок для этого промокода. "
                    "Промокод применяется только к активным подпискам с конечным сроком."
                ),
            )

    async with promos_uow:
        await promos_uow.promo_redemptions.create(
            promo_code=promo.code,
            user_id=user.id,
        )
        await promos_uow.commit()

    if has_effect:
        await apply_promo_to_targets(
            vpn_access_uow=vpn_access_uow,
            provisioning_gateway=provisioning_gateway,
            targets=targets,
            promo=promo,
        )

    logger.info(
        "promo_applied",
        telegram_id=telegram_id,
        code=normalized_code,
        bonus_days=promo.bonus_days,
        is_infinite=promo.is_infinite,
        apply_to_all=promo.apply_to_all,
        target_count=len(targets),
    )
    return PromoActivationResult(
        status=PromoActivationStatus.APPLIED,
        promo=promo,
        message="Промокод активирован ✨",
    )
