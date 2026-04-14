from datetime import datetime
from typing import Protocol
from uuid import UUID

from src.application.users.dto import TelegramUserData, UserProfile, UserSummary


class UsersRepository(Protocol):
    async def exists_by_telegram_id(self, telegram_id: int) -> bool: ...

    async def get_by_id(self, user_id: UUID) -> UserProfile | None: ...

    async def get_by_telegram_id(self, telegram_id: int) -> UserProfile | None: ...

    async def get_by_referral_code(self, referral_code: str) -> UserProfile | None: ...

    async def list_telegram_ids(self, *, has_vpn_access: bool | None) -> tuple[int, ...]: ...

    async def list_page(
        self,
        *,
        limit: int,
        offset: int,
        has_vpn_access: bool | None,
    ) -> tuple[UserSummary, ...]: ...

    async def search(self, query: str, limit: int) -> tuple[UserSummary, ...]: ...

    async def count_all(self) -> int: ...

    async def count_filtered(self, *, has_vpn_access: bool | None) -> int: ...

    async def count_with_vpn_access(self) -> int: ...

    async def count_created_since(self, created_from: datetime) -> int: ...

    async def count_premium(self) -> int: ...

    async def count_referrals(self, user_id: UUID, *, activated_only: bool = False) -> int: ...

    async def list_recent_referrals(
        self,
        user_id: UUID,
        limit: int,
    ) -> tuple[UserSummary, ...]: ...

    async def attach_referrer_if_eligible(
        self,
        user_id: UUID,
        *,
        referred_by_user_id: UUID,
    ) -> bool: ...

    async def create(
        self,
        data: TelegramUserData,
        *,
        referred_by_user_id: UUID | None = None,
    ) -> None: ...


class UsersUnitOfWork(Protocol):
    users: UsersRepository

    async def __aenter__(self) -> "UsersUnitOfWork": ...

    async def __aexit__(self, exc_type: object, exc: BaseException | None, tb: object) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
