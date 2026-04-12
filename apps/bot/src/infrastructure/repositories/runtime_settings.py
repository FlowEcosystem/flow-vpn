from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.runtime import AccessMode
from src.infrastructure.database.models import AppSettings


class SqlAlchemyRuntimeSettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_access_mode(self) -> AccessMode:
        settings = await self._get_or_create_settings()
        return settings.access_mode

    async def set_access_mode(self, access_mode: AccessMode) -> AccessMode:
        settings = await self._get_or_create_settings()
        settings.access_mode = access_mode
        await self._session.flush()
        return settings.access_mode

    async def _get_or_create_settings(self) -> AppSettings:
        stmt = select(AppSettings).where(AppSettings.id == 1)
        result = await self._session.execute(stmt)
        settings = result.scalar_one_or_none()
        if settings is not None:
            return settings

        settings = AppSettings(id=1, access_mode=AccessMode.FREE_ACCESS)
        self._session.add(settings)
        await self._session.flush()
        return settings
