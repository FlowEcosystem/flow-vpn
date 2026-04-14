"""Tests for VpnService.disable."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.application.vpn import VpnAccess
from src.application.vpn.use_cases import VpnService
from tests.conftest import (
    FakeRuntimeSettingsUnitOfWork,
    FakeUsersUnitOfWork,
    FakeVpnAccessUnitOfWork,
    build_access,
    build_user,
)


class FakeProvisioningGateway:
    def __init__(self, disabled_status: str = "disabled") -> None:
        self.disable_calls: list[str] = []
        self._disabled_status = disabled_status

    async def disable_vless_access(self, external_username: str) -> VpnAccess:
        self.disable_calls.append(external_username)
        now = datetime.now(UTC)
        # Return a minimal provisioned result that UpdateVpnAccessData accepts
        from src.application.vpn.dto import ProvisionedVpnAccess
        return ProvisionedVpnAccess(
            provider="marzban",
            status=self._disabled_status,
            external_username=external_username,
            subscription_url=None,
            vless_links=(),
            issued_at=now,
            expires_at=None,
        )

    async def provision_vless_access(self, *_):
        raise AssertionError("should not be called")

    async def enable_vless_access(self, *_):
        raise AssertionError("should not be called")

    async def reissue_vless_access(self, *_):
        raise AssertionError("should not be called")

    async def delete_vless_access(self, *_):
        raise AssertionError("should not be called")
# ── Tests ─────────────────────────────────────────────────────────────────────

def make_vpn_service(
    users_uow: FakeUsersUnitOfWork,
    vpn_uow: FakeVpnAccessUnitOfWork,
    gateway: FakeProvisioningGateway,
) -> VpnService:
    return VpnService(
        users_uow,
        FakeRuntimeSettingsUnitOfWork(),
        vpn_uow,
        gateway,
    )

@pytest.mark.asyncio
async def test_disable_active_access_calls_gateway_and_commits() -> None:
    user = build_user()
    access = build_access(user.id, status="active", username="tester_1")
    users_uow = FakeUsersUnitOfWork(user)
    vpn_uow = FakeVpnAccessUnitOfWork((access,))
    gateway = FakeProvisioningGateway()
    vpn = make_vpn_service(users_uow, vpn_uow, gateway)

    result = await vpn.disable(user.telegram_id, access.id)

    assert result is not None
    assert result.status == "disabled"
    assert gateway.disable_calls == [access.external_username]
    assert vpn_uow.commit_count == 1
    assert vpn_uow.vpn_access_events.created[0].event_type == "disabled_by_user"


@pytest.mark.asyncio
async def test_disable_already_inactive_access_skips_gateway() -> None:
    user = build_user()
    access = build_access(user.id, status="disabled", username="tester_1")
    users_uow = FakeUsersUnitOfWork(user)
    vpn_uow = FakeVpnAccessUnitOfWork((access,))
    gateway = FakeProvisioningGateway()
    vpn = make_vpn_service(users_uow, vpn_uow, gateway)

    result = await vpn.disable(user.telegram_id, access.id)

    assert result is not None
    assert result.status == "disabled"
    assert gateway.disable_calls == []
    assert vpn_uow.commit_count == 0


@pytest.mark.asyncio
async def test_disable_returns_none_for_unknown_user() -> None:
    users_uow = FakeUsersUnitOfWork(user=None)
    vpn_uow = FakeVpnAccessUnitOfWork()
    gateway = FakeProvisioningGateway()
    vpn = make_vpn_service(users_uow, vpn_uow, gateway)

    result = await vpn.disable(9999, uuid4())

    assert result is None
    assert gateway.disable_calls == []


@pytest.mark.asyncio
async def test_disable_returns_none_when_access_belongs_to_other_user() -> None:
    user = build_user()
    other_user = build_user(telegram_id=999)
    access = build_access(other_user.id, status="active", username="tester_1")
    users_uow = FakeUsersUnitOfWork(user)
    vpn_uow = FakeVpnAccessUnitOfWork((access,))
    gateway = FakeProvisioningGateway()
    vpn = make_vpn_service(users_uow, vpn_uow, gateway)

    result = await vpn.disable(user.telegram_id, access.id)

    assert result is None
    assert gateway.disable_calls == []
