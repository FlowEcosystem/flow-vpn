import uuid
from dataclasses import dataclass
from typing import Protocol

from src.application.support.dto import SupportTicketDetail, SupportTicketSummary


@dataclass(slots=True, frozen=True)
class SupportStats:
    closed_count: int
    average_rating: float | None
    total_ratings: int


class SupportTicketsRepository(Protocol):
    async def create(self, *, user_id: uuid.UUID, message: str) -> uuid.UUID: ...

    async def list_open(self, limit: int) -> tuple[SupportTicketSummary, ...]: ...

    async def get_detail(self, ticket_id: uuid.UUID) -> SupportTicketDetail | None: ...

    async def close(self, ticket_id: uuid.UUID) -> None: ...

    async def add_reply(
        self,
        *,
        ticket_id: uuid.UUID,
        admin_telegram_id: int,
        text: str,
    ) -> None: ...

    async def rate(self, ticket_id: uuid.UUID, rating: int) -> bool: ...

    async def get_stats(self) -> SupportStats: ...


class SupportUnitOfWork(Protocol):
    tickets: SupportTicketsRepository

    async def __aenter__(self) -> "SupportUnitOfWork": ...

    async def __aexit__(
        self,
        exc_type: object,
        exc: BaseException | None,
        tb: object,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
