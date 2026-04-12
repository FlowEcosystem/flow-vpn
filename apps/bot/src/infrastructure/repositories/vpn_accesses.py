from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.vpn import NewVpnAccessData, UpdateVpnAccessData, VpnAccess
from src.infrastructure.database.models import VpnAccess as VpnAccessModel


class SqlAlchemyVpnAccessRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: UUID) -> VpnAccess | None:
        stmt = select(VpnAccessModel).where(VpnAccessModel.user_id == user_id)
        result = await self._session.execute(stmt)
        access = result.scalar_one_or_none()
        if access is None:
            return None
        return self._map_model(access)

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
        return self._map_model(access)

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
        return self._map_model(access)

    def _map_model(self, access: VpnAccessModel) -> VpnAccess:
        return VpnAccess(
            id=access.id,
            user_id=access.user_id,
            provider=access.provider,
            status=access.status,
            external_username=access.external_username,
            subscription_url=access.subscription_url,
            vless_links=tuple(access.vless_links),
            issued_at=access.issued_at,
            expires_at=access.expires_at,
            created_at=access.created_at,
            updated_at=access.updated_at,
        )
