import uuid

import structlog

from src.application.broadcasts.dto import BroadcastSummary
from src.application.broadcasts.ports import BroadcastsUnitOfWork
from src.application.users.ports import UsersUnitOfWork

logger = structlog.get_logger(__name__)


def _segment_to_has_vpn_access(segment: str) -> bool | None:
    if segment == "with_access":
        return True
    if segment == "without_access":
        return False
    return None


class BroadcastsService:
    def __init__(
        self,
        broadcasts_uow: BroadcastsUnitOfWork,
        users_uow: UsersUnitOfWork,
    ) -> None:
        self._broadcasts_uow = broadcasts_uow
        self._users_uow = users_uow

    async def create(
        self,
        *,
        text: str,
        target_segment: str,
    ) -> tuple[BroadcastSummary, tuple[int, ...]]:
        has_vpn_access = _segment_to_has_vpn_access(target_segment)

        async with self._users_uow:
            telegram_ids = await self._users_uow.users.list_telegram_ids(
                has_vpn_access=has_vpn_access
            )

        async with self._broadcasts_uow as uow:
            summary = await uow.broadcasts.create(
                text=text,
                target_segment=target_segment,
                total_count=len(telegram_ids),
            )
            await uow.commit()

        logger.info(
            "broadcast_created",
            broadcast_id=str(summary.id),
            segment=target_segment,
            total_recipients=len(telegram_ids),
        )
        return summary, telegram_ids

    async def list_recent(self, limit: int = 20) -> tuple[BroadcastSummary, ...]:
        async with self._broadcasts_uow:
            return await self._broadcasts_uow.broadcasts.list_recent(limit)

    async def update_stats(
        self,
        broadcast_id: uuid.UUID,
        *,
        sent_count: int,
        failed_count: int,
    ) -> None:
        async with self._broadcasts_uow as uow:
            await uow.broadcasts.update_stats(
                broadcast_id,
                sent_count=sent_count,
                failed_count=failed_count,
            )
            await uow.commit()
        logger.info(
            "broadcast_completed",
            broadcast_id=str(broadcast_id),
            sent_count=sent_count,
            failed_count=failed_count,
        )
