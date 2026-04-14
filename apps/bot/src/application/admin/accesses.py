from uuid import UUID

import structlog

from src.application.admin.common import build_admin_user_detail, get_user_by_access_id
from src.application.admin.dto import AdminUserDetail
from src.application.users.ports import UsersUnitOfWork
from src.application.vpn import NewVpnAccessData, NewVpnAccessEventData, UpdateVpnAccessData
from src.application.vpn.ports import VpnAccessUnitOfWork, VpnProvisioningGateway

logger = structlog.get_logger(__name__)


async def issue_admin_access(
    *,
    users_uow: UsersUnitOfWork,
    vpn_access_uow: VpnAccessUnitOfWork,
    provisioning_gateway: VpnProvisioningGateway,
    telegram_id: int,
    actor_telegram_id: int,
    extra_event_details: dict[str, str] | None = None,
) -> AdminUserDetail | None:
    async with users_uow:
        user = await users_uow.users.get_by_telegram_id(telegram_id)

    if user is None:
        return None

    async with vpn_access_uow:
        existing_accesses = await vpn_access_uow.vpn_accesses.list_by_user_id(user.id)

    subscription_number = len(existing_accesses) + 1
    provisioned = await provisioning_gateway.provision_vless_access(
        user,
        subscription_number,
    )
    async with vpn_access_uow:
        access = await vpn_access_uow.vpn_accesses.create(
            NewVpnAccessData(
                user_id=user.id,
                provider=provisioned.provider,
                status=provisioned.status,
                external_username=provisioned.external_username,
                subscription_url=provisioned.subscription_url,
                vless_links=provisioned.vless_links,
                issued_at=provisioned.issued_at,
                expires_at=provisioned.expires_at,
            )
        )
        await vpn_access_uow.vpn_access_events.create(
            NewVpnAccessEventData(
                user_id=user.id,
                access_id=access.id,
                event_type="issued_by_admin",
                actor_telegram_id=actor_telegram_id,
                details={
                    "subscription_number": str(subscription_number),
                    "access_id": str(access.id),
                    **(extra_event_details or {}),
                },
            )
        )
        await vpn_access_uow.commit()

    logger.info(
        "admin_vpn_access_issued",
        target_telegram_id=telegram_id,
        actor_telegram_id=actor_telegram_id,
        access_id=str(access.id),
        subscription_number=subscription_number,
    )
    return await build_admin_user_detail(user=user, vpn_access_uow=vpn_access_uow)


async def enable_admin_access(
    *,
    users_uow: UsersUnitOfWork,
    vpn_access_uow: VpnAccessUnitOfWork,
    provisioning_gateway: VpnProvisioningGateway,
    access_id: UUID,
    actor_telegram_id: int,
    extra_event_details: dict[str, str] | None = None,
) -> AdminUserDetail | None:
    resolved = await get_user_by_access_id(
        access_id=access_id,
        users_uow=users_uow,
        vpn_access_uow=vpn_access_uow,
    )
    if resolved is None:
        return None
    user, access = resolved

    if access.status != "active":
        provisioned = await provisioning_gateway.enable_vless_access(access.external_username)
        async with vpn_access_uow:
            await vpn_access_uow.vpn_accesses.update(
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
                    event_type="enabled_by_admin",
                    actor_telegram_id=actor_telegram_id,
                    details={"access_id": str(access.id), **(extra_event_details or {})},
                )
            )
            await vpn_access_uow.commit()

        logger.info(
            "admin_vpn_access_enabled",
            actor_telegram_id=actor_telegram_id,
            access_id=str(access.id),
        )

    return await build_admin_user_detail(user=user, vpn_access_uow=vpn_access_uow)


async def disable_admin_access(
    *,
    users_uow: UsersUnitOfWork,
    vpn_access_uow: VpnAccessUnitOfWork,
    provisioning_gateway: VpnProvisioningGateway,
    access_id: UUID,
    actor_telegram_id: int,
    extra_event_details: dict[str, str] | None = None,
) -> AdminUserDetail | None:
    resolved = await get_user_by_access_id(
        access_id=access_id,
        users_uow=users_uow,
        vpn_access_uow=vpn_access_uow,
    )
    if resolved is None:
        return None
    user, access = resolved

    if access.status == "active":
        provisioned = await provisioning_gateway.disable_vless_access(access.external_username)
        async with vpn_access_uow:
            await vpn_access_uow.vpn_accesses.update(
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
                    event_type="disabled_by_admin",
                    actor_telegram_id=actor_telegram_id,
                    details={"access_id": str(access.id), **(extra_event_details or {})},
                )
            )
            await vpn_access_uow.commit()

        logger.info(
            "admin_vpn_access_disabled",
            actor_telegram_id=actor_telegram_id,
            access_id=str(access.id),
        )

    return await build_admin_user_detail(user=user, vpn_access_uow=vpn_access_uow)


async def reissue_admin_access(
    *,
    users_uow: UsersUnitOfWork,
    vpn_access_uow: VpnAccessUnitOfWork,
    provisioning_gateway: VpnProvisioningGateway,
    access_id: UUID,
    actor_telegram_id: int,
    extra_event_details: dict[str, str] | None = None,
) -> AdminUserDetail | None:
    resolved = await get_user_by_access_id(
        access_id=access_id,
        users_uow=users_uow,
        vpn_access_uow=vpn_access_uow,
    )
    if resolved is None:
        return None
    user, access = resolved

    provisioned = await provisioning_gateway.reissue_vless_access(access.external_username)
    async with vpn_access_uow:
        await vpn_access_uow.vpn_accesses.update(
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
                event_type="reissued_by_admin",
                actor_telegram_id=actor_telegram_id,
                details={"access_id": str(access.id), **(extra_event_details or {})},
            )
        )
        await vpn_access_uow.commit()

    logger.info(
        "admin_vpn_access_reissued",
        actor_telegram_id=actor_telegram_id,
        access_id=str(access.id),
    )
    return await build_admin_user_detail(user=user, vpn_access_uow=vpn_access_uow)


async def delete_admin_access(
    *,
    users_uow: UsersUnitOfWork,
    vpn_access_uow: VpnAccessUnitOfWork,
    provisioning_gateway: VpnProvisioningGateway,
    access_id: UUID,
    actor_telegram_id: int,
    extra_event_details: dict[str, str] | None = None,
) -> AdminUserDetail | None:
    resolved = await get_user_by_access_id(
        access_id=access_id,
        users_uow=users_uow,
        vpn_access_uow=vpn_access_uow,
    )
    if resolved is None:
        return None
    user, access = resolved

    await provisioning_gateway.delete_vless_access(access.external_username)
    async with vpn_access_uow:
        await vpn_access_uow.vpn_access_events.create(
            NewVpnAccessEventData(
                user_id=user.id,
                access_id=access.id,
                event_type="deleted_by_admin",
                actor_telegram_id=actor_telegram_id,
                details={
                    "external_username": access.external_username,
                    "access_id": str(access.id),
                    **(extra_event_details or {}),
                },
            )
        )
        await vpn_access_uow.vpn_accesses.delete(access.id)
        await vpn_access_uow.commit()

    logger.info(
        "admin_vpn_access_deleted",
        actor_telegram_id=actor_telegram_id,
        access_id=str(access.id),
    )
    return await build_admin_user_detail(user=user, vpn_access_uow=vpn_access_uow)
