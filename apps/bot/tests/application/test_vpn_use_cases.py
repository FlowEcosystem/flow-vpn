from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.application.users import UserProfile
from src.application.vpn import (
    AcquireVpnAccessOutcome,
    VpnAccess,
)
from src.application.vpn.use_cases import VpnService
from tests.conftest import (
    FakeRuntimeSettingsUnitOfWork,
    FakeUsersUnitOfWork,
    FakeVpnAccessUnitOfWork,
    build_access,
)


class FakeProvisioningGateway:
    def __init__(self) -> None:
        self.deleted_usernames: list[str] = []
        self.provision_calls: list[tuple[int, int]] = []

    async def provision_vless_access(self, user: UserProfile, subscription_number: int):
        self.provision_calls.append((user.telegram_id, subscription_number))
        raise AssertionError("provision_vless_access should not be called in the limit test")

    async def enable_vless_access(self, external_username: str):
        raise AssertionError

    async def disable_vless_access(self, external_username: str):
        raise AssertionError

    async def reissue_vless_access(self, external_username: str):
        raise AssertionError

    async def delete_vless_access(self, external_username: str) -> None:
        self.deleted_usernames.append(external_username)


def build_user() -> UserProfile:
    return UserProfile(
        id=uuid4(),
        telegram_id=123,
        referral_code="ref123",
        username="tester",
        first_name="Test",
        last_name=None,
        language_code="ru",
        is_premium=False,
        created_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_acquire_vpn_access_returns_limit_reached_when_user_hits_cap() -> None:
    user = build_user()
    existing_access = build_access(user.id, username="tester_1")
    users_uow = FakeUsersUnitOfWork(user)
    runtime_uow = FakeRuntimeSettingsUnitOfWork(max_vpn_accesses_per_user=1)
    vpn_uow = FakeVpnAccessUnitOfWork((existing_access,))
    provisioning_gateway = FakeProvisioningGateway()
    vpn = VpnService(
        users_uow,
        runtime_uow,
        vpn_uow,
        provisioning_gateway,
    )

    result = await vpn.acquire(user.telegram_id)

    assert result.outcome is AcquireVpnAccessOutcome.LIMIT_REACHED
    assert result.access is None
    assert provisioning_gateway.provision_calls == []


@pytest.mark.asyncio
async def test_delete_user_vpn_access_removes_provider_user_and_db_record() -> None:
    user = build_user()
    access = build_access(user.id, username="tester_1")
    users_uow = FakeUsersUnitOfWork(user)
    runtime_uow = FakeRuntimeSettingsUnitOfWork(max_vpn_accesses_per_user=1)
    vpn_uow = FakeVpnAccessUnitOfWork((access,))
    provisioning_gateway = FakeProvisioningGateway()
    vpn = VpnService(users_uow, runtime_uow, vpn_uow, provisioning_gateway)

    is_deleted = await vpn.delete(user.telegram_id, access.id)

    assert is_deleted is True
    assert provisioning_gateway.deleted_usernames == [access.external_username]
    assert vpn_uow.vpn_accesses.deleted_access_ids == [access.id]
    assert vpn_uow.vpn_access_events.created_events[0].event_type == "deleted_by_user"
    assert vpn_uow.commit_count == 1
