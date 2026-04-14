"""Shared test fixtures and fake building blocks."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.application.runtime import AccessMode
from src.application.users import TelegramUserData, UserProfile
from src.application.vpn import NewVpnAccessEventData, VpnAccess
from src.application.vpn.dto import NewVpnAccessData, UpdateVpnAccessData


def build_user(
    *,
    telegram_id: int = 42,
    username: str = "tester",
    has_referral: bool = False,
) -> UserProfile:
    return UserProfile(
        id=uuid4(),
        telegram_id=telegram_id,
        referral_code=f"ref{telegram_id}",
        username=username,
        first_name="Test",
        last_name=None,
        language_code="ru",
        is_premium=False,
        created_at=datetime.now(UTC),
    )


def build_telegram_user_data(telegram_id: int = 42) -> TelegramUserData:
    return TelegramUserData(
        telegram_id=telegram_id,
        username=f"user{telegram_id}",
        first_name="User",
        last_name=None,
        language_code="ru",
        is_bot=False,
        is_premium=False,
    )


class FakeUsersRepository:
    """Minimal in-memory users repository for use case tests."""

    def __init__(self, user: UserProfile | None = None) -> None:
        self._user = user

    async def get_by_id(self, user_id: UUID) -> UserProfile | None:
        if self._user and self._user.id == user_id:
            return self._user
        return None

    async def get_by_telegram_id(self, telegram_id: int) -> UserProfile | None:
        if self._user and self._user.telegram_id == telegram_id:
            return self._user
        return None

    async def get_by_referral_code(self, referral_code: str) -> UserProfile | None:
        if self._user and self._user.referral_code == referral_code:
            return self._user
        return None

    async def create(
        self, data: TelegramUserData, *, referred_by_user_id: UUID | None = None
    ) -> None:
        self._user = UserProfile(
            id=uuid4(),
            telegram_id=data.telegram_id,
            referral_code=f"ref{data.telegram_id}",
            username=data.username,
            first_name=data.first_name,
            last_name=data.last_name,
            language_code=data.language_code,
            is_premium=data.is_premium,
            created_at=datetime.now(UTC),
        )

    async def attach_referrer_if_eligible(
        self, user_id: UUID, *, referred_by_user_id: UUID
    ) -> bool:
        return False

    async def count_referrals(self, user_id: UUID, *, activated_only: bool = False) -> int:
        return 0

    async def list_recent_referrals(self, user_id: UUID, limit: int) -> tuple:
        return ()

    async def list_telegram_ids(self, *, has_vpn_access: bool | None = None) -> tuple[int, ...]:
        return (self._user.telegram_id,) if self._user else ()

    async def count_all(self) -> int:
        return 1 if self._user else 0

    async def count_filtered(self, *, has_vpn_access: bool | None) -> int:
        return 0

    async def count_with_vpn_access(self) -> int:
        return 0

    async def count_created_since(self, created_from: datetime) -> int:
        return 0

    async def count_premium(self) -> int:
        return 0

    async def list_page(self, *, limit: int, offset: int, has_vpn_access: bool | None) -> tuple:
        return ()

    async def search(self, query: str, limit: int) -> tuple:
        return ()


class FakeUsersUnitOfWork:
    def __init__(self, user: UserProfile | None = None) -> None:
        self.users = FakeUsersRepository(user)
        self.commit_count = 0

    async def __aenter__(self) -> "FakeUsersUnitOfWork":
        return self

    async def __aexit__(self, *_) -> None:
        pass

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        pass


class FakeRuntimeSettingsRepository:
    def __init__(
        self,
        access_mode: AccessMode = AccessMode.FREE_ACCESS,
        max_vpn_accesses_per_user: int = 1,
    ) -> None:
        self.access_mode = access_mode
        self.max_vpn_accesses_per_user = max_vpn_accesses_per_user

    async def get_access_mode(self) -> AccessMode:
        return self.access_mode

    async def set_access_mode(self, access_mode: AccessMode) -> AccessMode:
        self.access_mode = access_mode
        return self.access_mode

    async def get_max_vpn_accesses_per_user(self) -> int:
        return self.max_vpn_accesses_per_user

    async def set_max_vpn_accesses_per_user(self, limit: int) -> int:
        self.max_vpn_accesses_per_user = limit
        return self.max_vpn_accesses_per_user


class FakeRuntimeSettingsUnitOfWork:
    def __init__(
        self,
        access_mode: AccessMode = AccessMode.FREE_ACCESS,
        max_vpn_accesses_per_user: int = 1,
    ) -> None:
        self.settings = FakeRuntimeSettingsRepository(
            access_mode=access_mode,
            max_vpn_accesses_per_user=max_vpn_accesses_per_user,
        )
        self.commit_count = 0

    async def __aenter__(self) -> "FakeRuntimeSettingsUnitOfWork":
        return self

    async def __aexit__(self, *_) -> None:
        pass

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        pass


def build_access(
    user_id: UUID,
    *,
    username: str = "tester_1",
    status: str = "active",
    expires_at: datetime | None = None,
    created_at: datetime | None = None,
) -> VpnAccess:
    now = created_at or datetime.now(UTC)
    return VpnAccess(
        id=uuid4(),
        user_id=user_id,
        provider="marzban",
        status=status,
        external_username=username,
        subscription_url=f"https://sub.example/{username}",
        vless_links=(f"vless://{username}",),
        issued_at=now,
        expires_at=expires_at,
        created_at=now,
        updated_at=now,
    )


class FakeVpnAccessesRepository:
    def __init__(self, accesses: tuple[VpnAccess, ...] = ()) -> None:
        self._accesses: dict[UUID, VpnAccess] = {access.id: access for access in accesses}
        self._next_id = uuid4()
        self.updated: list[tuple[UUID, UpdateVpnAccessData]] = []
        self.deleted_access_ids: list[UUID] = []
        self.created_accesses: list[NewVpnAccessData] = []

    async def list_by_user_id(self, user_id: UUID) -> tuple[VpnAccess, ...]:
        return tuple(access for access in self._accesses.values() if access.user_id == user_id)

    async def get_by_id(self, access_id: UUID) -> VpnAccess | None:
        return self._accesses.get(access_id)

    async def get_by_user_id(self, user_id: UUID) -> VpnAccess | None:
        accesses = [access for access in self._accesses.values() if access.user_id == user_id]
        if not accesses:
            return None
        return max(accesses, key=lambda access: access.created_at)

    async def create(self, data: NewVpnAccessData) -> VpnAccess:
        now = datetime.now(UTC)
        access = VpnAccess(
            id=self._next_id,
            user_id=data.user_id,
            provider=data.provider,
            status=data.status,
            external_username=data.external_username,
            subscription_url=data.subscription_url,
            vless_links=tuple(data.vless_links),
            issued_at=data.issued_at,
            expires_at=data.expires_at,
            created_at=now,
            updated_at=now,
        )
        self.created_accesses.append(data)
        self._accesses[access.id] = access
        self._next_id = uuid4()
        return access

    async def update(self, access_id: UUID, data: UpdateVpnAccessData) -> VpnAccess:
        access = self._accesses[access_id]
        updated = VpnAccess(
            id=access.id,
            user_id=access.user_id,
            provider=access.provider,
            status=data.status,
            external_username=access.external_username,
            subscription_url=data.subscription_url,
            vless_links=tuple(data.vless_links),
            issued_at=data.issued_at,
            expires_at=data.expires_at,
            created_at=access.created_at,
            updated_at=datetime.now(UTC),
        )
        self._accesses[access_id] = updated
        self.updated.append((access_id, data))
        return updated

    async def delete(self, access_id: UUID) -> None:
        self.deleted_access_ids.append(access_id)
        self._accesses.pop(access_id, None)

    async def list_active_expired(self) -> tuple[VpnAccess, ...]:
        now = datetime.now(UTC)
        return tuple(
            access
            for access in self._accesses.values()
            if access.status == "active"
            and access.expires_at is not None
            and access.expires_at < now
        )


class FakeVpnAccessEventsRepository:
    def __init__(self) -> None:
        self.created: list[NewVpnAccessEventData] = []
        self.created_events = self.created

    async def create(self, data: NewVpnAccessEventData) -> NewVpnAccessEventData:
        self.created.append(data)
        return data

    async def list_by_user_id(
        self,
        user_id: UUID,
        limit: int,
    ) -> tuple[NewVpnAccessEventData, ...]:
        filtered = [event for event in self.created if event.user_id == user_id]
        return tuple(filtered[-limit:])


class FakeVpnAccessUnitOfWork:
    def __init__(self, accesses: tuple[VpnAccess, ...] = ()) -> None:
        self.vpn_accesses = FakeVpnAccessesRepository(accesses)
        self.vpn_access_events = FakeVpnAccessEventsRepository()
        self.commit_count = 0

    async def __aenter__(self) -> "FakeVpnAccessUnitOfWork":
        return self

    async def __aexit__(self, *_) -> None:
        pass

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        pass


@pytest.fixture
def user() -> UserProfile:
    return build_user()


@pytest.fixture
def users_uow(user: UserProfile) -> FakeUsersUnitOfWork:
    return FakeUsersUnitOfWork(user)
