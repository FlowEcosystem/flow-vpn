import pytest

from src.application.runtime import AccessMode
from src.application.runtime.use_cases import RuntimeSettingsService
from tests.conftest import FakeRuntimeSettingsUnitOfWork


# ── RuntimeSettingsService ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_access_mode_returns_current_mode() -> None:
    uow = FakeRuntimeSettingsUnitOfWork(access_mode=AccessMode.BILLING_ENABLED)
    result = await RuntimeSettingsService(uow).get_access_mode()
    assert result is AccessMode.BILLING_ENABLED


@pytest.mark.asyncio
async def test_set_access_mode_updates_and_commits() -> None:
    uow = FakeRuntimeSettingsUnitOfWork(access_mode=AccessMode.FREE_ACCESS)
    result = await RuntimeSettingsService(uow).set_access_mode(AccessMode.BILLING_ENABLED)

    assert result is AccessMode.BILLING_ENABLED
    assert uow.settings.access_mode is AccessMode.BILLING_ENABLED
    assert uow.commit_count == 1


@pytest.mark.asyncio
async def test_set_access_mode_idempotent_when_same_value() -> None:
    uow = FakeRuntimeSettingsUnitOfWork(access_mode=AccessMode.FREE_ACCESS)
    result = await RuntimeSettingsService(uow).set_access_mode(AccessMode.FREE_ACCESS)

    assert result is AccessMode.FREE_ACCESS
    assert uow.commit_count == 1


@pytest.mark.asyncio
async def test_get_max_vpn_accesses_returns_stored_value() -> None:
    uow = FakeRuntimeSettingsUnitOfWork(max_vpn_accesses_per_user=3)
    result = await RuntimeSettingsService(uow).get_max_vpn_accesses_per_user()
    assert result == 3


@pytest.mark.asyncio
async def test_set_max_vpn_accesses_updates_and_commits() -> None:
    uow = FakeRuntimeSettingsUnitOfWork(max_vpn_accesses_per_user=1)
    result = await RuntimeSettingsService(uow).set_max_vpn_accesses_per_user(5)

    assert result == 5
    assert uow.settings.max_vpn_accesses_per_user == 5
    assert uow.commit_count == 1


@pytest.mark.asyncio
async def test_set_max_vpn_accesses_clamps_negative_to_zero() -> None:
    uow = FakeRuntimeSettingsUnitOfWork(max_vpn_accesses_per_user=2)
    result = await RuntimeSettingsService(uow).set_max_vpn_accesses_per_user(-10)

    assert result == 0
    assert uow.settings.max_vpn_accesses_per_user == 0
