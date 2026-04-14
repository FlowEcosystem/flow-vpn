from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class PromoActivationStatus(StrEnum):
    APPLIED = "applied"
    ALREADY_USED = "already_used"
    NOT_FOUND = "not_found"
    INACTIVE = "inactive"
    NO_ELIGIBLE_ACCESSES = "no_eligible_accesses"


@dataclass(slots=True, frozen=True)
class PromoCodeInfo:
    code: str
    title: str
    description: str | None
    bonus_days: int
    is_infinite: bool
    apply_to_all: bool
    expires_at: datetime | None
    remaining_activations: int | None  # None = unlimited


@dataclass(slots=True, frozen=True)
class PromoOverview:
    total_activations: int
    recent_promos: tuple[PromoCodeInfo, ...]


@dataclass(slots=True, frozen=True)
class PromoActivationResult:
    status: PromoActivationStatus
    promo: PromoCodeInfo | None
    message: str


@dataclass(slots=True, frozen=True)
class AdminPromoDetail:
    id: UUID
    code: str
    title: str
    bonus_days: int
    is_infinite: bool
    apply_to_all: bool
    is_active: bool
    max_redemptions: int | None
    current_redemptions: int
    expires_at: datetime | None
    created_at: datetime


@dataclass(slots=True, frozen=True)
class EligibleVpnAccess:
    """Подписка, пригодная для применения промокода."""
    access_id: UUID
    number: int          # порядковый номер среди ВСЕХ подписок пользователя (1-based)
    expires_at: datetime  # всегда заполнен (бесконечные не включаются)


@dataclass(slots=True, frozen=True)
class PromoEligibility:
    promo: PromoCodeInfo | None          # None = не найден / истёк / исчерпан
    already_used: bool
    eligible_accesses: tuple[EligibleVpnAccess, ...]


@dataclass(slots=True, frozen=True)
class NewPromoCodeData:
    code: str
    title: str
    bonus_days: int
    is_infinite: bool
    apply_to_all: bool
    max_redemptions: int | None
