"""Tests for BroadcastsService."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.application.broadcasts.dto import BroadcastSummary
from src.application.broadcasts.use_cases import BroadcastsService
from tests.conftest import FakeUsersUnitOfWork, build_user

# ── Fakes ─────────────────────────────────────────────────────────────────────

class FakeBroadcastsRepository:
    def __init__(self) -> None:
        self.created: list[dict] = []
        self.stats_updated: list[dict] = []

    async def create(self, *, text: str, target_segment: str, total_count: int) -> BroadcastSummary:
        broadcast_id = uuid4()
        self.created.append(
            {"text": text, "segment": target_segment, "total_count": total_count}
        )
        return BroadcastSummary(
            id=broadcast_id,
            target_segment=target_segment,
            status="sending",
            total_count=total_count,
            sent_count=0,
            failed_count=0,
            created_at=datetime.now(UTC),
            completed_at=None,
        )

    async def update_stats(
        self, broadcast_id: UUID, *, sent_count: int, failed_count: int
    ) -> None:
        self.stats_updated.append(
            {"id": broadcast_id, "sent": sent_count, "failed": failed_count}
        )

    async def list_recent(self, limit: int) -> tuple:
        return ()


class FakeBroadcastsUnitOfWork:
    def __init__(self) -> None:
        self.broadcasts = FakeBroadcastsRepository()
        self.commit_count = 0

    async def __aenter__(self) -> "FakeBroadcastsUnitOfWork":
        return self

    async def __aexit__(self, *_) -> None:
        pass

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        pass


# ── BroadcastsService ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_broadcast_all_segment_targets_all_users() -> None:
    user = build_user()
    users_uow = FakeUsersUnitOfWork(user)
    broadcasts_uow = FakeBroadcastsUnitOfWork()
    service = BroadcastsService(broadcasts_uow, users_uow)

    summary, telegram_ids = await service.create(text="Hello!", target_segment="all")

    assert summary.target_segment == "all"
    assert summary.total_count == 1
    assert user.telegram_id in telegram_ids
    assert broadcasts_uow.commit_count == 1


@pytest.mark.asyncio
async def test_create_broadcast_persists_text_and_segment() -> None:
    user = build_user()
    users_uow = FakeUsersUnitOfWork(user)
    broadcasts_uow = FakeBroadcastsUnitOfWork()
    service = BroadcastsService(broadcasts_uow, users_uow)

    await service.create(text="Big news", target_segment="with_access")

    record = broadcasts_uow.broadcasts.created[0]
    assert record["text"] == "Big news"
    assert record["segment"] == "with_access"


@pytest.mark.asyncio
async def test_create_broadcast_returns_telegram_ids_for_targeting() -> None:
    user = build_user(telegram_id=55)
    users_uow = FakeUsersUnitOfWork(user)
    broadcasts_uow = FakeBroadcastsUnitOfWork()
    service = BroadcastsService(broadcasts_uow, users_uow)

    _, telegram_ids = await service.create(text="Hi", target_segment="all")

    assert 55 in telegram_ids


@pytest.mark.asyncio
async def test_update_stats_saves_sent_and_failed_counts() -> None:
    broadcasts_uow = FakeBroadcastsUnitOfWork()
    service = BroadcastsService(broadcasts_uow, FakeUsersUnitOfWork(user=None))
    broadcast_id = uuid4()

    await service.update_stats(broadcast_id, sent_count=90, failed_count=10)

    record = broadcasts_uow.broadcasts.stats_updated[0]
    assert record["id"] == broadcast_id
    assert record["sent"] == 90
    assert record["failed"] == 10
    assert broadcasts_uow.commit_count == 1
