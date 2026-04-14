# ruff: noqa: RUF001

from uuid import UUID

import structlog

from src.application.users.ports import UsersUnitOfWork
from src.application.vpn.dto import NewVpnAccessEventData, UpdateVpnAccessData, VpnAccess
from src.application.vpn.ports import VpnAccessUnitOfWork, VpnProvisioningGateway

logger = structlog.get_logger(__name__)


async def _resolve_user_access(
    *,
    users_uow: UsersUnitOfWork,
    vpn_access_uow: VpnAccessUnitOfWork,
    telegram_id: int,
    access_id: UUID,
) -> tuple[object, VpnAccess] | None:
    async with users_uow:
        user = await users_uow.users.get_by_telegram_id(telegram_id)

    if user is None:
        return None

    async with vpn_access_uow:
        access = await vpn_access_uow.vpn_accesses.get_by_id(access_id)

    if access is None or access.user_id != user.id:
        return None

    return user, access


async def enable_user_access(
    *,
    users_uow: UsersUnitOfWork,
    vpn_access_uow: VpnAccessUnitOfWork,
    provisioning_gateway: VpnProvisioningGateway,
    telegram_id: int,
    access_id: UUID,
) -> VpnAccess | None:
    resolved = await _resolve_user_access(
        users_uow=users_uow,
        vpn_access_uow=vpn_access_uow,
        telegram_id=telegram_id,
        access_id=access_id,
    )
    if resolved is None:
        return None
    user, access = resolved

    if access.status == "active":
        return access

    provisioned = await provisioning_gateway.enable_vless_access(access.external_username)
    async with vpn_access_uow:
        access = await vpn_access_uow.vpn_accesses.update(
            access.id,
            UpdateVpnAccessData(
                status=provisioned.status,
                subscription_url=provisioned.subscription_url,
                vless_links=provisioned.vless_links,
                issued_at=provisioned.issued_at,
                expires_at=provisioned.expires_at,
            ),
        )
        await vpn_access_uow.vpn_access_events.create(
            NewVpnAccessEventData(
                user_id=user.id,
                access_id=access.id,
                event_type="enabled_by_user",
                actor_telegram_id=user.telegram_id,
                details={},
            )
        )
        await vpn_access_uow.commit()

    logger.info("vpn_access_enabled", telegram_id=telegram_id, access_id=str(access_id))
    return access


async def disable_user_access(
    *,
    users_uow: UsersUnitOfWork,
    vpn_access_uow: VpnAccessUnitOfWork,
    provisioning_gateway: VpnProvisioningGateway,
    telegram_id: int,
    access_id: UUID,
) -> VpnAccess | None:
    resolved = await _resolve_user_access(
        users_uow=users_uow,
        vpn_access_uow=vpn_access_uow,
        telegram_id=telegram_id,
        access_id=access_id,
    )
    if resolved is None:
        return None
    user, access = resolved

    if access.status != "active":
        return access

    provisioned = await provisioning_gateway.disable_vless_access(access.external_username)
    async with vpn_access_uow:
        access = await vpn_access_uow.vpn_accesses.update(
            access.id,
            UpdateVpnAccessData(
                status=provisioned.status,
                subscription_url=provisioned.subscription_url,
                vless_links=provisioned.vless_links,
                issued_at=provisioned.issued_at,
                expires_at=provisioned.expires_at,
            ),
        )
        await vpn_access_uow.vpn_access_events.create(
            NewVpnAccessEventData(
                user_id=user.id,
                access_id=access.id,
                event_type="disabled_by_user",
                actor_telegram_id=user.telegram_id,
                details={},
            )
        )
        await vpn_access_uow.commit()

    logger.info("vpn_access_disabled", telegram_id=telegram_id, access_id=str(access_id))
    return access


async def delete_user_access(
    *,
    users_uow: UsersUnitOfWork,
    vpn_access_uow: VpnAccessUnitOfWork,
    provisioning_gateway: VpnProvisioningGateway,
    telegram_id: int,
    access_id: UUID,
) -> bool:
    resolved = await _resolve_user_access(
        users_uow=users_uow,
        vpn_access_uow=vpn_access_uow,
        telegram_id=telegram_id,
        access_id=access_id,
    )
    if resolved is None:
        return False
    user, access = resolved

    await provisioning_gateway.delete_vless_access(access.external_username)

    async with vpn_access_uow:
        await vpn_access_uow.vpn_access_events.create(
            NewVpnAccessEventData(
                user_id=user.id,
                access_id=access.id,
                event_type="deleted_by_user",
                actor_telegram_id=user.telegram_id,
                details={"external_username": access.external_username},
            )
        )
        await vpn_access_uow.vpn_accesses.delete(access.id)
        await vpn_access_uow.commit()

    logger.info("vpn_access_deleted", telegram_id=telegram_id, access_id=str(access_id))
    return True
