import uuid
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.application.support.use_cases import SupportService
from tests.conftest import FakeUsersUnitOfWork, build_user

# ── Fakes ─────────────────────────────────────────────────────────────────────

class FakeTicketsRepository:
    def __init__(self) -> None:
        self.created: list[dict] = []
        self.closed: list[UUID] = []
        self._tickets: dict[UUID, object] = {}

    async def create(self, *, user_id: UUID, message: str) -> uuid.UUID:
        ticket_id = uuid4()
        self.created.append({"user_id": user_id, "message": message, "id": ticket_id})
        return ticket_id

    async def get_detail(self, ticket_id: UUID):
        return self._tickets.get(ticket_id)

    async def close(self, ticket_id: UUID) -> None:
        self.closed.append(ticket_id)

    async def list_open(self, limit: int):
        return ()

    async def add_reply(self, *, ticket_id: UUID, admin_telegram_id: int, text: str) -> None:
        pass


class FakeSupportUnitOfWork:
    def __init__(self, tickets: FakeTicketsRepository | None = None) -> None:
        self.tickets = tickets or FakeTicketsRepository()
        self.commit_count = 0

    async def __aenter__(self) -> "FakeSupportUnitOfWork":
        return self

    async def __aexit__(self, *_) -> None:
        pass

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        pass


class FakeSettings:
    support_url = None
    support_title = None


# ── SupportService ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_ticket_creates_and_returns_id() -> None:
    user = build_user()
    users_uow = FakeUsersUnitOfWork(user)
    tickets_repo = FakeTicketsRepository()
    support_uow = FakeSupportUnitOfWork(tickets_repo)
    service = SupportService(FakeSettings(), users_uow, support_uow)

    ticket_id = await service.create_ticket(user.telegram_id, message="My VPN stopped working")

    assert ticket_id is not None
    assert isinstance(ticket_id, uuid.UUID)
    assert tickets_repo.created[0]["user_id"] == user.id
    assert tickets_repo.created[0]["message"] == "My VPN stopped working"
    assert support_uow.commit_count == 1


@pytest.mark.asyncio
async def test_create_ticket_unknown_user_returns_none() -> None:
    users_uow = FakeUsersUnitOfWork(user=None)
    support_uow = FakeSupportUnitOfWork()
    service = SupportService(FakeSettings(), users_uow, support_uow)

    ticket_id = await service.create_ticket(9999, message="Help!")

    assert ticket_id is None
    assert support_uow.commit_count == 0


@pytest.mark.asyncio
async def test_close_ticket_marks_existing_ticket_as_closed() -> None:
    from src.application.support.dto import SupportTicketDetail

    ticket_id = uuid4()
    tickets_repo = FakeTicketsRepository()
    tickets_repo._tickets[ticket_id] = SupportTicketDetail(
        id=ticket_id,
        user_telegram_id=77,
        user_first_name="Help",
        user_username="supporter",
        message="My VPN stopped working",
        status="open",
        replies=(),
        created_at=datetime.now(UTC),
    )
    support_uow = FakeSupportUnitOfWork(tickets_repo)
    service = SupportService(FakeSettings(), FakeUsersUnitOfWork(user=None), support_uow)

    result = await service.close_ticket(ticket_id)

    assert result is True
    assert ticket_id in tickets_repo.closed
    assert support_uow.commit_count == 1


@pytest.mark.asyncio
async def test_close_ticket_returns_false_for_missing_ticket() -> None:
    support_uow = FakeSupportUnitOfWork()
    service = SupportService(FakeSettings(), FakeUsersUnitOfWork(user=None), support_uow)

    result = await service.close_ticket(uuid4())

    assert result is False
    assert support_uow.commit_count == 0
