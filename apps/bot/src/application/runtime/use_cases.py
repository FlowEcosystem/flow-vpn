import structlog

from src.application.runtime.dto import AccessMode
from src.application.runtime.ports import RuntimeSettingsUnitOfWork

logger = structlog.get_logger(__name__)


class RuntimeSettingsService:
    def __init__(self, uow: RuntimeSettingsUnitOfWork) -> None:
        self._uow = uow

    async def get_access_mode(self) -> AccessMode:
        async with self._uow:
            return await self._uow.settings.get_access_mode()

    async def set_access_mode(self, access_mode: AccessMode) -> AccessMode:
        async with self._uow:
            updated_mode = await self._uow.settings.set_access_mode(access_mode)
            await self._uow.commit()
        logger.info("access_mode_changed", mode=updated_mode.value)
        return updated_mode

    async def get_max_vpn_accesses_per_user(self) -> int:
        async with self._uow:
            return await self._uow.settings.get_max_vpn_accesses_per_user()

    async def set_max_vpn_accesses_per_user(self, limit: int) -> int:
        normalized_limit = max(0, limit)
        async with self._uow:
            updated_limit = await self._uow.settings.set_max_vpn_accesses_per_user(
                normalized_limit
            )
            await self._uow.commit()
        logger.info("max_vpn_accesses_changed", limit=updated_limit)
        return updated_limit
