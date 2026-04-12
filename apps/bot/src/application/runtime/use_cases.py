from src.application.runtime.dto import AccessMode
from src.application.runtime.ports import RuntimeSettingsUnitOfWork


class GetAccessModeUseCase:
    def __init__(self, uow: RuntimeSettingsUnitOfWork) -> None:
        self._uow = uow

    async def execute(self) -> AccessMode:
        async with self._uow:
            return await self._uow.settings.get_access_mode()


class SetAccessModeUseCase:
    def __init__(self, uow: RuntimeSettingsUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, access_mode: AccessMode) -> AccessMode:
        async with self._uow:
            updated_mode = await self._uow.settings.set_access_mode(access_mode)
            await self._uow.commit()
            return updated_mode
