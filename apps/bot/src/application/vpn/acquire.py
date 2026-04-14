# ruff: noqa: RUF001

import structlog

from src.application.runtime import AccessMode
from src.application.runtime.ports import RuntimeSettingsUnitOfWork
from src.application.users.ports import UsersUnitOfWork
from src.application.vpn.dto import (
    AcquireVpnAccessOutcome,
    AcquireVpnAccessResult,
    NewVpnAccessData,
    NewVpnAccessEventData,
)
from src.application.vpn.ports import VpnAccessUnitOfWork, VpnProvisioningGateway

logger = structlog.get_logger(__name__)


async def acquire_vpn_access(
    *,
    users_uow: UsersUnitOfWork,
    runtime_settings_uow: RuntimeSettingsUnitOfWork,
    vpn_access_uow: VpnAccessUnitOfWork,
    provisioning_gateway: VpnProvisioningGateway,
    telegram_id: int,
) -> AcquireVpnAccessResult:
    async with users_uow:
        user = await users_uow.users.get_by_telegram_id(telegram_id)

    if user is None:
        logger.warning("vpn_access_acquire_failed", reason="user_not_found", telegram_id=telegram_id)
        return AcquireVpnAccessResult(
            outcome=AcquireVpnAccessOutcome.USER_NOT_FOUND,
            message="Профиль не найден. Отправьте /start ещё раз.",
        )

    async with runtime_settings_uow:
        access_mode = await runtime_settings_uow.settings.get_access_mode()
        max_vpn_accesses_per_user = (
            await runtime_settings_uow.settings.get_max_vpn_accesses_per_user()
        )

    if access_mode is AccessMode.BILLING_ENABLED:
        logger.info("vpn_access_acquire_blocked", reason="billing_required", telegram_id=telegram_id)
        return AcquireVpnAccessResult(
            outcome=AcquireVpnAccessOutcome.BILLING_REQUIRED,
            message=(
                "Сейчас подключение оформляется по подписке. "
                "Скоро здесь появится выбор тарифа."
            ),
        )

    async with vpn_access_uow:
        existing_accesses = await vpn_access_uow.vpn_accesses.list_by_user_id(user.id)

    if 0 < max_vpn_accesses_per_user <= len(existing_accesses):
        logger.info(
            "vpn_access_acquire_blocked",
            reason="limit_reached",
            telegram_id=telegram_id,
            current_count=len(existing_accesses),
            limit=max_vpn_accesses_per_user,
        )
        return AcquireVpnAccessResult(
            outcome=AcquireVpnAccessOutcome.LIMIT_REACHED,
            message=(
                "Достигнут лимит подписок для одного аккаунта. "
                "Удалите ненужную подписку или обратитесь в поддержку."
            ),
        )

    subscription_number = len(existing_accesses) + 1

    try:
        provisioned_access = await provisioning_gateway.provision_vless_access(
            user,
            subscription_number,
        )
    except ValueError:
        logger.warning(
            "vpn_provisioning_failed",
            reason="provider_not_configured",
            telegram_id=telegram_id,
        )
        return AcquireVpnAccessResult(
            outcome=AcquireVpnAccessOutcome.PROVIDER_NOT_CONFIGURED,
            message=(
                "Сейчас выдача доступа временно недоступна. "
                "Попробуйте чуть позже или напишите в поддержку."
            ),
        )
    except RuntimeError:
        logger.error("vpn_provisioning_failed", reason="provider_error", telegram_id=telegram_id)
        return AcquireVpnAccessResult(
            outcome=AcquireVpnAccessOutcome.PROVIDER_ERROR,
            message=(
                "Не удалось подготовить подключение прямо сейчас. "
                "Попробуйте ещё раз немного позже."
            ),
        )

    async with vpn_access_uow:
        access = await vpn_access_uow.vpn_accesses.create(
            NewVpnAccessData(
                user_id=user.id,
                provider=provisioned_access.provider,
                status=provisioned_access.status,
                external_username=provisioned_access.external_username,
                subscription_url=provisioned_access.subscription_url,
                vless_links=provisioned_access.vless_links,
                issued_at=provisioned_access.issued_at,
                expires_at=provisioned_access.expires_at,
            )
        )
        await vpn_access_uow.vpn_access_events.create(
            NewVpnAccessEventData(
                user_id=user.id,
                access_id=access.id,
                event_type="issued",
                actor_telegram_id=user.telegram_id,
                details={"source": "user_flow"},
            )
        )
        await vpn_access_uow.commit()

    logger.info(
        "vpn_access_acquired",
        telegram_id=telegram_id,
        access_id=str(access.id),
        provider=provisioned_access.provider,
    )
    return AcquireVpnAccessResult(
        outcome=AcquireVpnAccessOutcome.ACTIVE,
        access=access,
    )
