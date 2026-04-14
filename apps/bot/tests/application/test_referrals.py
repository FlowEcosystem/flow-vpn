from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.application.referrals.use_cases import ReferralsService
from src.application.users import TelegramUserData, UserProfile, UserSummary
from src.application.users.use_cases import UsersService


class FakeUsersRepository:
    def __init__(self) -> None:
        now = datetime.now(UTC)
        self.profiles: dict[int, UserProfile] = {}
        self.has_vpn_access: dict[UUID, bool] = {}
        self.referred_by: dict[UUID, UUID | None] = {}
        self.created_users: list[UserProfile] = []
        self.attach_calls: list[tuple[UUID, UUID]] = []
        self._seed_user(
            telegram_id=100,
            referral_code="ref100",
            username="referrer",
            first_name="Ref",
            referred_by_user_id=None,
            has_vpn_access=True,
            created_at=now,
        )

    async def exists_by_telegram_id(self, telegram_id: int) -> bool:
        return telegram_id in self.profiles

    async def get_by_telegram_id(self, telegram_id: int) -> UserProfile | None:
        return self.profiles.get(telegram_id)

    async def get_by_referral_code(self, referral_code: str) -> UserProfile | None:
        for profile in self.profiles.values():
            if profile.referral_code == referral_code:
                return profile
        return None

    async def count_referrals(self, user_id: UUID, *, activated_only: bool = False) -> int:
        referrals = [
            profile
            for profile in self.profiles.values()
            if self.referred_by.get(profile.id) == user_id
        ]
        if activated_only:
            referrals = [
                profile for profile in referrals
                if self.has_vpn_access.get(profile.id, False)
            ]
        return len(referrals)

    async def list_recent_referrals(self, user_id: UUID, limit: int) -> tuple[UserSummary, ...]:
        referrals = [
            profile
            for profile in self.profiles.values()
            if self.referred_by.get(profile.id) == user_id
        ]
        referrals.sort(key=lambda item: item.created_at, reverse=True)
        return tuple(
            UserSummary(
                id=profile.id,
                telegram_id=profile.telegram_id,
                username=profile.username,
                first_name=profile.first_name,
                last_name=profile.last_name,
                is_premium=profile.is_premium,
                created_at=profile.created_at,
                has_vpn_access=self.has_vpn_access.get(profile.id, False),
            )
            for profile in referrals[:limit]
        )

    async def attach_referrer_if_eligible(
        self,
        user_id: UUID,
        *,
        referred_by_user_id: UUID,
    ) -> bool:
        self.attach_calls.append((user_id, referred_by_user_id))
        for _telegram_id, profile in self.profiles.items():
            if profile.id != user_id:
                continue
            if self.referred_by.get(profile.id) is not None:
                return False
            if self.has_vpn_access.get(profile.id, False):
                return False
            self.referred_by[profile.id] = referred_by_user_id
            return True
        return False

    async def create(
        self,
        data: TelegramUserData,
        *,
        referred_by_user_id: UUID | None = None,
    ) -> None:
        profile = self._seed_user(
            telegram_id=data.telegram_id,
            referral_code=f"code{data.telegram_id}",
            username=data.username,
            first_name=data.first_name,
            referred_by_user_id=referred_by_user_id,
            has_vpn_access=False,
            created_at=datetime.now(UTC),
            last_name=data.last_name,
            language_code=data.language_code,
            is_premium=data.is_premium,
        )
        self.created_users.append(profile)

    async def list_page(self, *, limit: int, offset: int, has_vpn_access: bool | None):
        raise NotImplementedError

    async def search(self, query: str, limit: int):
        raise NotImplementedError

    async def count_all(self) -> int:
        raise NotImplementedError

    async def count_filtered(self, *, has_vpn_access: bool | None) -> int:
        raise NotImplementedError

    async def count_with_vpn_access(self) -> int:
        raise NotImplementedError

    async def count_created_since(self, created_from: datetime) -> int:
        raise NotImplementedError

    async def count_premium(self) -> int:
        raise NotImplementedError

    def _seed_user(
        self,
        *,
        telegram_id: int,
        referral_code: str,
        username: str | None,
        first_name: str | None,
        referred_by_user_id: UUID | None,
        has_vpn_access: bool,
        created_at: datetime,
        last_name: str | None = None,
        language_code: str | None = "ru",
        is_premium: bool | None = False,
    ) -> UserProfile:
        profile = UserProfile(
            id=uuid4(),
            telegram_id=telegram_id,
            referral_code=referral_code,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            is_premium=is_premium,
            created_at=created_at,
        )
        self.profiles[telegram_id] = profile
        self.has_vpn_access[profile.id] = has_vpn_access
        self.referred_by[profile.id] = referred_by_user_id
        return profile


class FakeUsersUnitOfWork:
    def __init__(self, users: FakeUsersRepository) -> None:
        self.users = users
        self.commit_count = 0

    async def __aenter__(self) -> "FakeUsersUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        return None


def build_telegram_user_data(telegram_id: int) -> TelegramUserData:
    return TelegramUserData(
        telegram_id=telegram_id,
        username=f"user{telegram_id}",
        first_name="User",
        last_name=None,
        language_code="ru",
        is_bot=False,
        is_premium=False,
    )


@pytest.mark.asyncio
async def test_register_new_user_with_referral_code_sets_referrer() -> None:
    users = FakeUsersRepository()
    uow = FakeUsersUnitOfWork(users)
    service = UsersService(uow)

    is_new = await service.register(build_telegram_user_data(200), referral_code="REF100")

    assert is_new is True
    assert users.created_users[-1].telegram_id == 200
    assert users.referred_by[users.created_users[-1].id] == users.profiles[100].id
    assert uow.commit_count == 1


@pytest.mark.asyncio
async def test_existing_user_can_attach_referrer_before_first_vpn_activation() -> None:
    users = FakeUsersRepository()
    waiting_user = users._seed_user(
        telegram_id=200,
        referral_code="code200",
        username="invitee",
        first_name="Invitee",
        referred_by_user_id=None,
        has_vpn_access=False,
        created_at=datetime.now(UTC),
    )
    uow = FakeUsersUnitOfWork(users)
    service = UsersService(uow)

    is_new = await service.register(build_telegram_user_data(200), referral_code="ref100")

    assert is_new is False
    assert users.attach_calls == [(waiting_user.id, users.profiles[100].id)]
    assert users.referred_by[users.profiles[200].id] == users.profiles[100].id
    assert uow.commit_count == 1


@pytest.mark.asyncio
async def test_existing_user_with_vpn_keeps_referrer_unchanged() -> None:
    users = FakeUsersRepository()
    activated_user = users._seed_user(
        telegram_id=200,
        referral_code="code200",
        username="invitee",
        first_name="Invitee",
        referred_by_user_id=None,
        has_vpn_access=True,
        created_at=datetime.now(UTC),
    )
    uow = FakeUsersUnitOfWork(users)
    service = UsersService(uow)

    is_new = await service.register(build_telegram_user_data(200), referral_code="ref100")

    assert is_new is False
    assert users.attach_calls == [(activated_user.id, users.profiles[100].id)]
    assert users.referred_by[users.profiles[200].id] is None
    assert uow.commit_count == 0


@pytest.mark.asyncio
async def test_referral_overview_separates_activated_and_pending_referrals() -> None:
    users = FakeUsersRepository()
    referrer = users.profiles[100]
    users._seed_user(
        telegram_id=200,
        referral_code="code200",
        username="active_friend",
        first_name="Active",
        referred_by_user_id=referrer.id,
        has_vpn_access=True,
        created_at=datetime(2026, 4, 12, 10, 0, tzinfo=UTC),
    )
    users._seed_user(
        telegram_id=201,
        referral_code="code201",
        username="waiting_friend",
        first_name="Waiting",
        referred_by_user_id=referrer.id,
        has_vpn_access=False,
        created_at=datetime(2026, 4, 12, 11, 0, tzinfo=UTC),
    )
    uow = FakeUsersUnitOfWork(users)
    service = ReferralsService(uow)

    overview = await service.get_overview(100)

    assert overview is not None
    assert overview.activated_referrals == 1
    assert overview.pending_referrals == 1
    assert overview.recent_referrals[0].username == "waiting_friend"
    assert overview.recent_referrals[0].has_activated_vpn is False
    assert overview.recent_referrals[1].username == "active_friend"
    assert overview.recent_referrals[1].has_activated_vpn is True
