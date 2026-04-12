from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


@dataclass(slots=True, frozen=True)
class VpnAccess:
    id: UUID
    user_id: UUID
    provider: str
    status: str
    external_username: str
    subscription_url: str
    vless_links: tuple[str, ...]
    issued_at: datetime
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True, frozen=True)
class NewVpnAccessData:
    user_id: UUID
    provider: str
    status: str
    external_username: str
    subscription_url: str
    vless_links: tuple[str, ...]
    issued_at: datetime
    expires_at: datetime | None


@dataclass(slots=True, frozen=True)
class UpdateVpnAccessData:
    status: str
    subscription_url: str
    vless_links: tuple[str, ...]
    issued_at: datetime
    expires_at: datetime | None


@dataclass(slots=True, frozen=True)
class ProvisionedVpnAccess:
    provider: str
    status: str
    external_username: str
    subscription_url: str
    vless_links: tuple[str, ...]
    issued_at: datetime
    expires_at: datetime | None


@dataclass(slots=True, frozen=True)
class VpnAccessEvent:
    id: UUID
    user_id: UUID
    access_id: UUID | None
    event_type: str
    actor_telegram_id: int | None
    details: dict[str, str]
    created_at: datetime


@dataclass(slots=True, frozen=True)
class NewVpnAccessEventData:
    user_id: UUID
    access_id: UUID | None
    event_type: str
    actor_telegram_id: int | None
    details: dict[str, str]


class AcquireVpnAccessOutcome(StrEnum):
    ACTIVE = "active"
    BILLING_REQUIRED = "billing_required"
    USER_NOT_FOUND = "user_not_found"
    PROVIDER_NOT_CONFIGURED = "provider_not_configured"
    PROVIDER_ERROR = "provider_error"


@dataclass(slots=True, frozen=True)
class AcquireVpnAccessResult:
    outcome: AcquireVpnAccessOutcome
    access: VpnAccess | None = None
    message: str | None = None
