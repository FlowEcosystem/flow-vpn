import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.broadcasts.dto import BroadcastSummary
from src.infrastructure.database.models.broadcast import Broadcast


class SqlAlchemyBroadcastsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        text: str,
        target_segment: str,
        total_count: int,
    ) -> BroadcastSummary:
        broadcast = Broadcast(
            text=text,
            target_segment=target_segment,
            total_count=total_count,
            status="sending",
        )
        self._session.add(broadcast)
        await self._session.flush()
        await self._session.refresh(broadcast)
        return self._map(broadcast)

    async def list_recent(self, limit: int) -> tuple[BroadcastSummary, ...]:
        stmt = (
            select(Broadcast)
            .order_by(Broadcast.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return tuple(self._map(b) for b in result.scalars().all())

    async def update_stats(
        self,
        broadcast_id: uuid.UUID,
        *,
        sent_count: int,
        failed_count: int,
    ) -> None:
        stmt = (
            update(Broadcast)
            .where(Broadcast.id == broadcast_id)
            .values(
                status="done",
                sent_count=sent_count,
                failed_count=failed_count,
                completed_at=datetime.now(UTC),
            )
        )
        await self._session.execute(stmt)
        await self._session.flush()

    def _map(self, broadcast: Broadcast) -> BroadcastSummary:
        return BroadcastSummary(
            id=broadcast.id,
            target_segment=broadcast.target_segment,
            status=broadcast.status,
            total_count=broadcast.total_count,
            sent_count=broadcast.sent_count,
            failed_count=broadcast.failed_count,
            created_at=broadcast.created_at,
            completed_at=broadcast.completed_at,
        )
