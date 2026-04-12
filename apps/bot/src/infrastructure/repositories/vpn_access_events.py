from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.vpn import NewVpnAccessEventData, VpnAccessEvent
from src.infrastructure.database.models import VpnAccessEvent as VpnAccessEventModel


class SqlAlchemyVpnAccessEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: NewVpnAccessEventData) -> VpnAccessEvent:
        event = VpnAccessEventModel(
            user_id=data.user_id,
            access_id=data.access_id,
            event_type=data.event_type,
            actor_telegram_id=data.actor_telegram_id,
            details=data.details,
        )
        self._session.add(event)
        await self._session.flush()
        return self._map_model(event)

    async def list_by_user_id(self, user_id: UUID, limit: int) -> tuple[VpnAccessEvent, ...]:
        stmt = (
            select(VpnAccessEventModel)
            .where(VpnAccessEventModel.user_id == user_id)
            .order_by(VpnAccessEventModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return tuple(self._map_model(event) for event in result.scalars().all())

    def _map_model(self, event: VpnAccessEventModel) -> VpnAccessEvent:
        return VpnAccessEvent(
            id=event.id,
            user_id=event.user_id,
            access_id=event.access_id,
            event_type=event.event_type,
            actor_telegram_id=event.actor_telegram_id,
            details=event.details,
            created_at=event.created_at,
        )
