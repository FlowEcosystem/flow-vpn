import uuid
from typing import Protocol

from src.application.broadcasts.dto import BroadcastSummary


class BroadcastsRepository(Protocol):
    async def create(
        self,
        *,
        text: str,
        target_segment: str,
        total_count: int,
    ) -> BroadcastSummary: ...

    async def list_recent(self, limit: int) -> tuple[BroadcastSummary, ...]: ...

    async def update_stats(
        self,
        broadcast_id: uuid.UUID,
        *,
        sent_count: int,
        failed_count: int,
    ) -> None: ...


class BroadcastsUnitOfWork(Protocol):
    broadcasts: BroadcastsRepository

    async def __aenter__(self) -> "BroadcastsUnitOfWork": ...

    async def __aexit__(
        self,
        exc_type: object,
        exc: BaseException | None,
        tb: object,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
