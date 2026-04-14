from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from src.application.promos.dto import (
    AdminPromoDetail,
    NewPromoCodeData,
    PromoActivationStatus,
    PromoCodeInfo,
)
from src.application.promos.use_cases import PromoService
from src.application.vpn.dto import ProvisionedVpnAccess, UpdateVpnAccessData, VpnAccess
from tests.conftest import FakeUsersUnitOfWork, FakeVpnAccessUnitOfWork, build_access, build_user


class FakePromoCodesRepository:
    def __init__(
        self,
        promos: list[PromoCodeInfo] | None = None,
        existing_ids: set[UUID] | None = None,
    ) -> None:
        self._promos: dict[str, PromoCodeInfo] = {p.code: p for p in (promos or [])}
        self._existing_ids = existing_ids or set()
        self.created: list[NewPromoCodeData] = []
        self.deleted: list[UUID] = []
        self.toggled: list[tuple[UUID, bool]] = []

    async def get_active_by_code(self, code: str) -> PromoCodeInfo | None:
        return self._promos.get(code)

    async def create(self, data: NewPromoCodeData) -> AdminPromoDetail:
        self.created.append(data)
        promo_id = uuid4()
        self._existing_ids.add(promo_id)
        return AdminPromoDetail(
            id=promo_id,
            code=data.code,
            title=data.title,
            bonus_days=data.bonus_days,
            is_infinite=data.is_infinite,
            apply_to_all=data.apply_to_all,
            is_active=True,
            max_redemptions=data.max_redemptions,
            current_redemptions=0,
            expires_at=None,
            created_at=datetime.now(UTC),
        )

    async def get_by_id(self, promo_id: UUID) -> AdminPromoDetail | None:
        if promo_id not in self._existing_ids:
            return None
        return AdminPromoDetail(
            id=promo_id,
            code="PROMO",
            title="Test",
            bonus_days=7,
            is_infinite=False,
            apply_to_all=False,
            is_active=True,
            max_redemptions=None,
            current_redemptions=0,
            expires_at=None,
            created_at=datetime.now(UTC),
        )

    async def set_active(self, promo_id: UUID, *, is_active: bool) -> None:
        self.toggled.append((promo_id, is_active))

    async def delete(self, promo_id: UUID) -> None:
        self.deleted.append(promo_id)
        self._existing_ids.discard(promo_id)

    async def list_all(self, limit: int) -> tuple[AdminPromoDetail, ...]:
        return ()

    async def list_recent_active(self, limit: int) -> tuple[PromoCodeInfo, ...]:
        return ()


class FakePromoRedemptionsRepository:
    def __init__(self, existing: set[tuple[str, UUID]] | None = None) -> None:
        self._existing: set[tuple[str, UUID]] = existing or set()
        self.created: list[tuple[str, UUID]] = []

    async def exists(self, *, promo_code: str, user_id: UUID) -> bool:
        return (promo_code, user_id) in self._existing

    async def create(self, *, promo_code: str, user_id: UUID) -> None:
        self.created.append((promo_code, user_id))
        self._existing.add((promo_code, user_id))

    async def count_by_user_id(self, user_id: UUID) -> int:
        return sum(1 for _, uid in self._existing if uid == user_id)


class FakePromosUnitOfWork:
    def __init__(
        self,
        promo_codes: FakePromoCodesRepository,
        promo_redemptions: FakePromoRedemptionsRepository,
    ) -> None:
        self.promo_codes = promo_codes
        self.promo_redemptions = promo_redemptions
        self.commit_count = 0

    async def __aenter__(self) -> "FakePromosUnitOfWork":
        return self

    async def __aexit__(self, *_: object) -> None:
        pass

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        pass


class FakeProvisioningGateway:
    def __init__(self) -> None:
        self.extend_calls: list[tuple[str, int]] = []
        self.infinite_calls: list[str] = []

    async def extend_vless_access(
        self,
        external_username: str,
        bonus_days: int,
    ) -> ProvisionedVpnAccess:
        self.extend_calls.append((external_username, bonus_days))
        now = datetime.now(UTC)
        return ProvisionedVpnAccess(
            provider="marzban",
            status="active",
            external_username=external_username,
            subscription_url=f"https://sub.example/{external_username}",
            vless_links=(f"vless://{external_username}",),
            issued_at=now,
            expires_at=now + timedelta(days=bonus_days),
        )

    async def make_vless_access_infinite(self, external_username: str) -> ProvisionedVpnAccess:
        self.infinite_calls.append(external_username)
        now = datetime.now(UTC)
        return ProvisionedVpnAccess(
            provider="marzban",
            status="active",
            external_username=external_username,
            subscription_url=f"https://sub.example/{external_username}",
            vless_links=(f"vless://{external_username}",),
            issued_at=now,
            expires_at=None,
        )

    async def provision_vless_access(self, *_: object) -> ProvisionedVpnAccess:
        raise AssertionError("should not be called")

    async def enable_vless_access(self, *_: object) -> ProvisionedVpnAccess:
        raise AssertionError("should not be called")

    async def disable_vless_access(self, *_: object) -> ProvisionedVpnAccess:
        raise AssertionError("should not be called")

    async def reissue_vless_access(self, *_: object) -> ProvisionedVpnAccess:
        raise AssertionError("should not be called")

    async def delete_vless_access(self, *_: object) -> None:
        raise AssertionError("should not be called")


def build_promo(
    code: str = "SUMMER10",
    *,
    bonus_days: int = 10,
    is_infinite: bool = False,
    apply_to_all: bool = False,
) -> PromoCodeInfo:
    return PromoCodeInfo(
        code=code,
        title="Summer promo",
        description=None,
        bonus_days=bonus_days,
        is_infinite=is_infinite,
        apply_to_all=apply_to_all,
        expires_at=None,
        remaining_activations=None,
    )


def make_promos_uow(
    promos: list[PromoCodeInfo] | None = None,
    redemptions: set[tuple[str, UUID]] | None = None,
    existing_ids: set[UUID] | None = None,
) -> FakePromosUnitOfWork:
    return FakePromosUnitOfWork(
        promo_codes=FakePromoCodesRepository(promos, existing_ids),
        promo_redemptions=FakePromoRedemptionsRepository(redemptions),
    )


@pytest.mark.asyncio
async def test_apply_promo_valid_code_applies_and_commits() -> None:
    user = build_user()
    access = build_access(
        user.id,
        username="tester_1",
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )
    users_uow = FakeUsersUnitOfWork(user)
    promos_uow = make_promos_uow(promos=[build_promo("SUMMER10")])
    vpn_uow = FakeVpnAccessUnitOfWork((access,))
    gateway = FakeProvisioningGateway()
    promos = PromoService(users_uow, promos_uow, vpn_uow, gateway)

    result = await promos.apply(user.telegram_id, code="summer10")

    assert result.status is PromoActivationStatus.APPLIED
    assert result.promo is not None
    assert result.promo.code == "SUMMER10"
    assert promos_uow.promo_redemptions.created == [("SUMMER10", user.id)]
    assert promos_uow.commit_count == 1
    assert gateway.extend_calls == [("tester_1", 10)]
    assert vpn_uow.commit_count == 1
    assert vpn_uow.vpn_accesses.updated[0][0] == access.id


@pytest.mark.asyncio
async def test_apply_promo_normalises_code_to_upper() -> None:
    user = build_user()
    access = build_access(
        user.id,
        username="tester_1",
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )
    users_uow = FakeUsersUnitOfWork(user)
    promos_uow = make_promos_uow(promos=[build_promo("WINTER20")])
    vpn_uow = FakeVpnAccessUnitOfWork((access,))
    gateway = FakeProvisioningGateway()
    promos = PromoService(users_uow, promos_uow, vpn_uow, gateway)

    result = await promos.apply(user.telegram_id, code="  winter20  ")

    assert result.status is PromoActivationStatus.APPLIED
    assert promos_uow.promo_redemptions.created == [("WINTER20", user.id)]


@pytest.mark.asyncio
async def test_apply_promo_unknown_code_returns_not_found() -> None:
    user = build_user()
    users_uow = FakeUsersUnitOfWork(user)
    promos_uow = make_promos_uow()
    vpn_uow = FakeVpnAccessUnitOfWork()
    gateway = FakeProvisioningGateway()
    promos = PromoService(users_uow, promos_uow, vpn_uow, gateway)

    result = await promos.apply(user.telegram_id, code="NOPE")

    assert result.status is PromoActivationStatus.NOT_FOUND
    assert result.promo is None
    assert promos_uow.commit_count == 0


@pytest.mark.asyncio
async def test_apply_promo_already_used_returns_already_used() -> None:
    user = build_user()
    users_uow = FakeUsersUnitOfWork(user)
    promos_uow = make_promos_uow(
        promos=[build_promo("REPEAT")],
        redemptions={("REPEAT", user.id)},
    )
    vpn_uow = FakeVpnAccessUnitOfWork()
    gateway = FakeProvisioningGateway()
    promos = PromoService(users_uow, promos_uow, vpn_uow, gateway)

    result = await promos.apply(user.telegram_id, code="REPEAT")

    assert result.status is PromoActivationStatus.ALREADY_USED
    assert promos_uow.commit_count == 0


@pytest.mark.asyncio
async def test_apply_promo_empty_code_raises_value_error() -> None:
    user = build_user()
    users_uow = FakeUsersUnitOfWork(user)
    promos_uow = make_promos_uow()
    vpn_uow = FakeVpnAccessUnitOfWork()
    gateway = FakeProvisioningGateway()
    promos = PromoService(users_uow, promos_uow, vpn_uow, gateway)

    with pytest.raises(ValueError):
        await promos.apply(user.telegram_id, code="   ")


@pytest.mark.asyncio
async def test_apply_promo_unknown_user_returns_not_found() -> None:
    users_uow = FakeUsersUnitOfWork(user=None)
    promos_uow = make_promos_uow(promos=[build_promo("CODE")])
    vpn_uow = FakeVpnAccessUnitOfWork()
    gateway = FakeProvisioningGateway()
    promos = PromoService(users_uow, promos_uow, vpn_uow, gateway)

    result = await promos.apply(9999, code="CODE")

    assert result.status is PromoActivationStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_apply_promo_applies_to_selected_access() -> None:
    user = build_user()
    first_access = build_access(
        user.id,
        username="tester_1",
        expires_at=datetime.now(UTC) + timedelta(days=10),
        created_at=datetime.now(UTC),
    )
    second_access = build_access(
        user.id,
        username="tester_2",
        expires_at=datetime.now(UTC) + timedelta(days=20),
        created_at=datetime.now(UTC) + timedelta(minutes=1),
    )
    users_uow = FakeUsersUnitOfWork(user)
    promos_uow = make_promos_uow(promos=[build_promo("TARGET10")])
    vpn_uow = FakeVpnAccessUnitOfWork((first_access, second_access))
    gateway = FakeProvisioningGateway()
    promos = PromoService(users_uow, promos_uow, vpn_uow, gateway)

    result = await promos.apply(
        user.telegram_id,
        code="TARGET10",
        target_access_id=second_access.id,
    )

    assert result.status is PromoActivationStatus.APPLIED
    assert gateway.extend_calls == [("tester_2", 10)]
    assert [access_id for access_id, _ in vpn_uow.vpn_accesses.updated] == [second_access.id]


@pytest.mark.asyncio
async def test_apply_promo_rejects_infinite_target_access() -> None:
    user = build_user()
    finite_access = build_access(
        user.id,
        username="tester_1",
        expires_at=datetime.now(UTC) + timedelta(days=20),
    )
    infinite_access = build_access(
        user.id,
        username="tester_2",
        expires_at=None,
    )
    users_uow = FakeUsersUnitOfWork(user)
    promos_uow = make_promos_uow(promos=[build_promo("NO_INFINITY", is_infinite=True)])
    vpn_uow = FakeVpnAccessUnitOfWork((finite_access, infinite_access))
    gateway = FakeProvisioningGateway()
    promos = PromoService(users_uow, promos_uow, vpn_uow, gateway)

    result = await promos.apply(
        user.telegram_id,
        code="NO_INFINITY",
        target_access_id=infinite_access.id,
    )

    assert result.status is PromoActivationStatus.NO_ELIGIBLE_ACCESSES
    assert promos_uow.commit_count == 0
    assert promos_uow.promo_redemptions.created == []
    assert gateway.infinite_calls == []


@pytest.mark.asyncio
async def test_apply_promo_requires_explicit_target_when_multiple_eligible() -> None:
    user = build_user()
    first_access = build_access(
        user.id,
        username="tester_1",
        expires_at=datetime.now(UTC) + timedelta(days=20),
    )
    second_access = build_access(
        user.id,
        username="tester_2",
        expires_at=datetime.now(UTC) + timedelta(days=25),
    )
    users_uow = FakeUsersUnitOfWork(user)
    promos_uow = make_promos_uow(promos=[build_promo("CHOOSE")])
    vpn_uow = FakeVpnAccessUnitOfWork((first_access, second_access))
    gateway = FakeProvisioningGateway()
    promos = PromoService(users_uow, promos_uow, vpn_uow, gateway)

    result = await promos.apply(user.telegram_id, code="CHOOSE")

    assert result.status is PromoActivationStatus.NO_ELIGIBLE_ACCESSES
    assert "выбрать подписку" in result.message.lower()
    assert promos_uow.commit_count == 0
    assert vpn_uow.commit_count == 0


@pytest.mark.asyncio
async def test_apply_promo_apply_to_all_ignores_target_and_updates_all_eligible() -> None:
    user = build_user()
    first_access = build_access(
        user.id,
        username="tester_1",
        expires_at=datetime.now(UTC) + timedelta(days=20),
    )
    second_access = build_access(
        user.id,
        username="tester_2",
        expires_at=datetime.now(UTC) + timedelta(days=25),
    )
    infinite_access = build_access(
        user.id,
        username="tester_3",
        expires_at=None,
    )
    users_uow = FakeUsersUnitOfWork(user)
    promos_uow = make_promos_uow(promos=[build_promo("ALL", apply_to_all=True)])
    vpn_uow = FakeVpnAccessUnitOfWork((first_access, second_access, infinite_access))
    gateway = FakeProvisioningGateway()
    promos = PromoService(users_uow, promos_uow, vpn_uow, gateway)

    result = await promos.apply(
        user.telegram_id,
        code="ALL",
        target_access_id=first_access.id,
    )

    assert result.status is PromoActivationStatus.APPLIED
    assert gateway.extend_calls == [("tester_1", 10), ("tester_2", 10)]
    assert [access_id for access_id, _ in vpn_uow.vpn_accesses.updated] == [
        first_access.id,
        second_access.id,
    ]


@pytest.mark.asyncio
async def test_check_promo_eligibility_returns_only_active_finite_accesses_with_numbers() -> None:
    user = build_user()
    base = datetime.now(UTC)
    first_finite = build_access(
        user.id,
        username="tester_1",
        expires_at=base + timedelta(days=10),
        created_at=base,
    )
    inactive_finite = build_access(
        user.id,
        username="tester_2",
        status="disabled",
        expires_at=base + timedelta(days=20),
        created_at=base + timedelta(minutes=1),
    )
    infinite_active = build_access(
        user.id,
        username="tester_3",
        expires_at=None,
        created_at=base + timedelta(minutes=2),
    )
    second_finite = build_access(
        user.id,
        username="tester_4",
        expires_at=base + timedelta(days=30),
        created_at=base + timedelta(minutes=3),
    )
    users_uow = FakeUsersUnitOfWork(user)
    promos_uow = make_promos_uow(promos=[build_promo("ELIGIBLE")])
    vpn_uow = FakeVpnAccessUnitOfWork(
        (first_finite, inactive_finite, infinite_active, second_finite)
    )
    promos = PromoService(users_uow, promos_uow, vpn_uow, FakeProvisioningGateway())

    result = await promos.check_eligibility(user.telegram_id, code="ELIGIBLE")

    assert result.promo is not None
    assert result.already_used is False
    assert [access.number for access in result.eligible_accesses] == [1, 4]
    assert [access.access_id for access in result.eligible_accesses] == [
        first_finite.id,
        second_finite.id,
    ]


@pytest.mark.asyncio
async def test_create_promo_persists_and_returns_detail() -> None:
    promos_uow = make_promos_uow()
    promos = PromoService(
        FakeUsersUnitOfWork(user=None),
        promos_uow,
        FakeVpnAccessUnitOfWork(),
        FakeProvisioningGateway(),
    )
    data = NewPromoCodeData(
        code="newcode",
        title="New",
        bonus_days=5,
        is_infinite=False,
        apply_to_all=False,
        max_redemptions=100,
    )

    result = await promos.create_promo(data)

    assert promos_uow.promo_codes.created[0].code == "newcode"
    assert promos_uow.commit_count == 1
    assert result.bonus_days == 5
    assert result.is_infinite is False
    assert result.apply_to_all is False


@pytest.mark.asyncio
async def test_toggle_promo_records_correct_state() -> None:
    promo_id = uuid4()
    promos_uow = make_promos_uow(existing_ids={promo_id})
    promos = PromoService(
        FakeUsersUnitOfWork(user=None),
        promos_uow,
        FakeVpnAccessUnitOfWork(),
        FakeProvisioningGateway(),
    )

    await promos.toggle_promo(promo_id, is_active=False)

    assert promos_uow.promo_codes.toggled == [(promo_id, False)]
    assert promos_uow.commit_count == 1


@pytest.mark.asyncio
async def test_delete_promo_removes_existing_promo() -> None:
    promo_id = uuid4()
    promos_uow = make_promos_uow(existing_ids={promo_id})
    promos = PromoService(
        FakeUsersUnitOfWork(user=None),
        promos_uow,
        FakeVpnAccessUnitOfWork(),
        FakeProvisioningGateway(),
    )

    result = await promos.delete_promo(promo_id)

    assert result is True
    assert promo_id in promos_uow.promo_codes.deleted
    assert promos_uow.commit_count == 1
