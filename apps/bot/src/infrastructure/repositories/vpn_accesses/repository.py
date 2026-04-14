from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.vpn import NewVpnAccessData, UpdateVpnAccessData, VpnAccess
from src.infrastructure.database.models import VpnAccess as VpnAccessModel
from src.infrastructure.repositories.vpn_accesses.mappers import map_vpn_access


class SqlAlchemyVpnAccessRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, access_id: UUID) -> VpnAccess | None:
        stmt = select(VpnAccessModel).where(VpnAccessModel.id == access_id)
        result = await self._session.execute(stmt)
        access = result.scalar_one_or_none()
        if access is None:
            return None
        return map_vpn_access(access)

    async def get_by_user_id(self, user_id: UUID) -> VpnAccess | None:
        stmt = (
            select(VpnAccessModel)
            .where(VpnAccessModel.user_id == user_id)
            .order_by(VpnAccessModel.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        access = result.scalar_one_or_none()
        if access is None:
            return None
        return map_vpn_access(access)

    async def list_by_user_id(self, user_id: UUID) -> tuple[VpnAccess, ...]:
        stmt = (
            select(VpnAccessModel)
            .where(VpnAccessModel.user_id == user_id)
            .order_by(VpnAccessModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return tuple(map_vpn_access(row) for row in result.scalars().all())

    async def create(self, data: NewVpnAccessData) -> VpnAccess:
        access = VpnAccessModel(
            user_id=data.user_id,
            provider=data.provider,
            status=data.status,
            external_username=data.external_username,
            subscription_url=data.subscription_url,
            vless_links=list(data.vless_links),
            issued_at=data.issued_at,
            expires_at=data.expires_at,
        )
        self._session.add(access)
        await self._session.flush()
        await self._session.refresh(access)
        return map_vpn_access(access)

    async def update(self, access_id: UUID, data: UpdateVpnAccessData) -> VpnAccess:
        stmt = select(VpnAccessModel).where(VpnAccessModel.id == access_id)
        result = await self._session.execute(stmt)
        access = result.scalar_one()
        access.status = data.status
        access.subscription_url = data.subscription_url
        access.vless_links = list(data.vless_links)
        access.issued_at = data.issued_at
        access.expires_at = data.expires_at
        await self._session.flush()
        await self._session.refresh(access)
        return map_vpn_access(access)

    async def delete(self, access_id: UUID) -> None:
        stmt = select(VpnAccessModel).where(VpnAccessModel.id == access_id)
        result = await self._session.execute(stmt)
        access = result.scalar_one_or_none()
        if access is None:
            return
        await self._session.delete(access)
        await self._session.flush()

    async def list_active_expired(self) -> tuple[VpnAccess, ...]:
        now = datetime.now(UTC)
        stmt = (
            select(VpnAccessModel)
            .where(VpnAccessModel.status == "active")
            .where(VpnAccessModel.expires_at.isnot(None))
            .where(VpnAccessModel.expires_at < now)
        )
        result = await self._session.execute(stmt)
        return tuple(map_vpn_access(row) for row in result.scalars().all())
