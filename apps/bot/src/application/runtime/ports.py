from typing import Protocol

from src.application.runtime.dto import AccessMode


class RuntimeSettingsRepository(Protocol):
    async def get_access_mode(self) -> AccessMode: ...

    async def set_access_mode(self, access_mode: AccessMode) -> AccessMode: ...


class RuntimeSettingsUnitOfWork(Protocol):
    settings: RuntimeSettingsRepository

    async def __aenter__(self) -> "RuntimeSettingsUnitOfWork": ...

    async def __aexit__(self, exc_type: object, exc: BaseException | None, tb: object) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
