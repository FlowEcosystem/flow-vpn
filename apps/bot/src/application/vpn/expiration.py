# ruff: noqa: RUF001

import structlog

from src.application.vpn.dto import NewVpnAccessEventData, UpdateVpnAccessData
from src.application.vpn.ports import VpnAccessUnitOfWork

logger = structlog.get_logger(__name__)


async def expire_vpn_accesses(*, vpn_access_uow: VpnAccessUnitOfWork) -> int:
    async with vpn_access_uow as uow:
        expired = await uow.vpn_accesses.list_active_expired()
        for access in expired:
            await uow.vpn_accesses.update(
                access.id,
                UpdateVpnAccessData(
                    status="disabled",
                    subscription_url=access.subscription_url,
                    vless_links=access.vless_links,
                    issued_at=access.issued_at,
                    expires_at=access.expires_at,
                ),
            )
            await uow.vpn_access_events.create(
                NewVpnAccessEventData(
                    user_id=access.user_id,
                    access_id=access.id,
                    event_type="expired_automatically",
                    actor_telegram_id=None,
                    details={},
                )
            )
        if expired:
            await uow.commit()

    if expired:
        logger.info("vpn_accesses_expired_automatically", count=len(expired))
    return len(expired)
