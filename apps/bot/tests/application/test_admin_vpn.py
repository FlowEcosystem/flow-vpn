"""Tests for admin VPN use cases with multi-access support."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.application.admin.dto import AdminUsersFilter
from src.application.admin.use_cases import AdminService
from src.application.users import UserSummary
from src.application.vpn import VpnAccess
from src.application.vpn.dto import ProvisionedVpnAccess
from tests.conftest import (
    FakeRuntimeSettingsUnitOfWork,
    FakeUsersUnitOfWork,
    FakeVpnAccessUnitOfWork,
    build_access,
    build_user,
)


class FakeProvisioningGateway:
    def __init__(self) -> None:
        self.provision_calls: list[str] = []
        self.enable_calls: list[str] = []
        self.disable_calls: list[str] = []
        self.reissue_calls: list[str] = []
        self.delete_calls: list[str] = []

    def _make_provisioned(self, username: str, status: str) -> ProvisionedVpnAccess:
        now = datetime.now(UTC)
        return ProvisionedVpnAccess(
            provider="marzban",
            status=status,
            external_username=username,
            subscription_url=f"https://sub.example/{username}",
            vless_links=(f"vless://{username}",),
            issued_at=now,
            expires_at=None,
        )

    async def provision_vless_access(self, user, subscription_number: int) -> ProvisionedVpnAccess:
        username = f"{user.username}_{subscription_number}"
        self.provision_calls.append(username)
        return self._make_provisioned(username, "active")

    async def enable_vless_access(self, external_username: str) -> ProvisionedVpnAccess:
        self.enable_calls.append(external_username)
        return self._make_provisioned(external_username, "active")

    async def disable_vless_access(self, external_username: str) -> ProvisionedVpnAccess:
        self.disable_calls.append(external_username)
        return self._make_provisioned(external_username, "disabled")

    async def reissue_vless_access(self, external_username: str) -> ProvisionedVpnAccess:
        self.reissue_calls.append(external_username)
        return self._make_provisioned(external_username, "active")

    async def delete_vless_access(self, external_username: str) -> None:
        self.delete_calls.append(external_username)


class FakeUsersOverviewRepository:
    def __init__(self, users: tuple[UserSummary, ...]) -> None:
        self._users = users

    async def count_all(self) -> int:
        return len(self._users)

    async def count_with_vpn_access(self) -> int:
        return sum(1 for user in self._users if user.has_vpn_access)

    async def count_filtered(self, *, has_vpn_access: bool | None) -> int:
        return len(self._filter_users(has_vpn_access))

    async def list_page(
        self,
        *,
        limit: int,
        offset: int,
        has_vpn_access: bool | None,
    ) -> tuple[UserSummary, ...]:
        filtered = self._filter_users(has_vpn_access)
        return tuple(filtered[offset : offset + limit])

    def _filter_users(self, has_vpn_access: bool | None) -> list[UserSummary]:
        if has_vpn_access is None:
            return list(self._users)
        return [user for user in self._users if user.has_vpn_access is has_vpn_access]


class FakeUsersOverviewUnitOfWork:
    def __init__(self, users: tuple[UserSummary, ...]) -> None:
        self.users = FakeUsersOverviewRepository(users)

    async def __aenter__(self) -> "FakeUsersOverviewUnitOfWork":
        return self

    async def __aexit__(self, *_: object) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass


def make_admin_service(
    users_uow,
    vpn_uow: FakeVpnAccessUnitOfWork,
    gateway: FakeProvisioningGateway,
) -> AdminService:
    return AdminService(
        users_uow=users_uow,
        runtime_settings_uow=FakeRuntimeSettingsUnitOfWork(),
        vpn_access_uow=vpn_uow,
        provisioning_gateway=gateway,
    )
@pytest.mark.asyncio
async def test_get_admin_user_detail_returns_all_accesses_sorted_by_creation() -> None:
    user = build_user()
    older = build_access(user.id, username="tester_1", created_at=datetime(2026, 1, 1, tzinfo=UTC))
    newer = build_access(user.id, username="tester_2", created_at=datetime(2026, 1, 2, tzinfo=UTC))
    users_uow = FakeUsersUnitOfWork(user)
    vpn_uow = FakeVpnAccessUnitOfWork((newer, older))
    admin = make_admin_service(users_uow, vpn_uow, FakeProvisioningGateway())

    result = await admin.get_user_detail(user.telegram_id)

    assert result is not None
    assert [access.external_username for access in result.vpn_accesses] == ["tester_1", "tester_2"]
    assert result.vpn_access is newer


@pytest.mark.asyncio
async def test_issue_always_creates_new_access() -> None:
    user = build_user()
    existing = build_access(user.id, username="tester_1", status="disabled")
    users_uow = FakeUsersUnitOfWork(user)
    vpn_uow = FakeVpnAccessUnitOfWork((existing,))
    gateway = FakeProvisioningGateway()
    admin = make_admin_service(users_uow, vpn_uow, gateway)

    result = await admin.issue_access(user.telegram_id, actor_telegram_id=1)

    assert result is not None
    assert gateway.provision_calls == [f"{user.username}_2"]
    assert [access.external_username for access in result.vpn_accesses] == ["tester_1", f"{user.username}_2"]
    assert vpn_uow.vpn_access_events.created[-1].event_type == "issued_by_admin"
    assert vpn_uow.commit_count == 1


@pytest.mark.asyncio
async def test_issue_returns_none_for_unknown_user() -> None:
    users_uow = FakeUsersUnitOfWork(user=None)
    vpn_uow = FakeVpnAccessUnitOfWork()
    gateway = FakeProvisioningGateway()
    admin = make_admin_service(users_uow, vpn_uow, gateway)

    result = await admin.issue_access(9999, actor_telegram_id=1)

    assert result is None


@pytest.mark.asyncio
async def test_enable_admin_enables_specific_access() -> None:
    user = build_user()
    disabled = build_access(user.id, username="tester_1", status="disabled")
    users_uow = FakeUsersUnitOfWork(user)
    vpn_uow = FakeVpnAccessUnitOfWork((disabled,))
    gateway = FakeProvisioningGateway()
    admin = make_admin_service(users_uow, vpn_uow, gateway)

    result = await admin.enable_access(disabled.id, actor_telegram_id=1)

    assert result is not None
    assert gateway.enable_calls == [disabled.external_username]
    assert result.vpn_accesses[0].status == "active"
    assert vpn_uow.vpn_access_events.created[-1].event_type == "enabled_by_admin"


@pytest.mark.asyncio
async def test_get_admin_users_overview_clamps_to_last_existing_page() -> None:
    users = tuple(
        UserSummary(
            id=uuid4(),
            telegram_id=1000 + index,
            username=f"user_{index}",
            first_name=f"User {index}",
            last_name=None,
            is_premium=False,
            created_at=datetime(2026, 1, index + 1, tzinfo=UTC),
            has_vpn_access=bool(index % 2),
        )
        for index in range(7)
    )
    users_uow = FakeUsersOverviewUnitOfWork(users)
    admin = make_admin_service(
        users_uow,
        FakeVpnAccessUnitOfWork(),
        FakeProvisioningGateway(),
    )

    result = await admin.get_users_overview(
        page=99,
        page_size=3,
        current_filter=AdminUsersFilter.ALL,
    )

    assert result.current_page == 2
    assert len(result.recent_users) == 1
    assert result.total_filtered == 7
    assert result.has_next_page is False


@pytest.mark.asyncio
async def test_disable_admin_disables_only_target_access() -> None:
    user = build_user()
    active = build_access(user.id, username="tester_1", status="active")
    other = build_access(user.id, username="tester_2", status="active")
    users_uow = FakeUsersUnitOfWork(user)
    vpn_uow = FakeVpnAccessUnitOfWork((active, other))
    gateway = FakeProvisioningGateway()
    admin = make_admin_service(users_uow, vpn_uow, gateway)

    result = await admin.disable_access(active.id, actor_telegram_id=1)

    assert result is not None
    assert gateway.disable_calls == [active.external_username]
    statuses = {access.external_username: access.status for access in result.vpn_accesses}
    assert statuses["tester_1"] == "disabled"
    assert statuses["tester_2"] == "active"
    assert vpn_uow.vpn_access_events.created[-1].event_type == "disabled_by_admin"


@pytest.mark.asyncio
async def test_reissue_admin_reissues_specific_access() -> None:
    user = build_user()
    access = build_access(user.id, username="tester_1", status="active")
    users_uow = FakeUsersUnitOfWork(user)
    vpn_uow = FakeVpnAccessUnitOfWork((access,))
    gateway = FakeProvisioningGateway()
    admin = make_admin_service(users_uow, vpn_uow, gateway)

    result = await admin.reissue_access(access.id, actor_telegram_id=1)

    assert result is not None
    assert gateway.reissue_calls == [access.external_username]
    assert vpn_uow.vpn_access_events.created[-1].event_type == "reissued_by_admin"
    assert vpn_uow.commit_count == 1


@pytest.mark.asyncio
async def test_delete_admin_deletes_specific_access() -> None:
    user = build_user()
    first = build_access(user.id, username="tester_1")
    second = build_access(user.id, username="tester_2")
    users_uow = FakeUsersUnitOfWork(user)
    vpn_uow = FakeVpnAccessUnitOfWork((first, second))
    gateway = FakeProvisioningGateway()
    admin = make_admin_service(users_uow, vpn_uow, gateway)

    result = await admin.delete_access(first.id, actor_telegram_id=1)

    assert result is not None
    assert gateway.delete_calls == [first.external_username]
    assert [access.external_username for access in result.vpn_accesses] == ["tester_2"]
    assert vpn_uow.vpn_access_events.created[-1].event_type == "deleted_by_admin"
    assert vpn_uow.commit_count == 1


@pytest.mark.asyncio
async def test_access_operations_return_none_for_unknown_access() -> None:
    user = build_user()
    users_uow = FakeUsersUnitOfWork(user)
    vpn_uow = FakeVpnAccessUnitOfWork()
    gateway = FakeProvisioningGateway()
    admin = make_admin_service(users_uow, vpn_uow, gateway)

    assert await admin.enable_access(
        uuid4(),
        actor_telegram_id=1,
    ) is None
    assert await admin.disable_access(
        uuid4(),
        actor_telegram_id=1,
    ) is None
    assert await admin.reissue_access(
        uuid4(),
        actor_telegram_id=1,
    ) is None
    assert await admin.delete_access(
        uuid4(),
        actor_telegram_id=1,
    ) is None
