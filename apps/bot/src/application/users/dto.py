from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True, frozen=True)
class TelegramUserData:
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    language_code: str | None
    is_bot: bool
    is_premium: bool | None


@dataclass(slots=True, frozen=True)
class UserProfile:
    id: UUID
    telegram_id: int
    referral_code: str
    username: str | None
    first_name: str | None
    last_name: str | None
    language_code: str | None
    is_premium: bool | None
    created_at: datetime


@dataclass(slots=True, frozen=True)
class UserSummary:
    id: UUID
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    is_premium: bool | None
    created_at: datetime
    has_vpn_access: bool
