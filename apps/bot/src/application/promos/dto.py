from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class PromoActivationStatus(StrEnum):
    APPLIED = "applied"
    ALREADY_USED = "already_used"
    NOT_FOUND = "not_found"
    INACTIVE = "inactive"


@dataclass(slots=True, frozen=True)
class PromoCodeInfo:
    code: str
    title: str
    description: str | None
    bonus_days: int
    expires_at: datetime | None


@dataclass(slots=True, frozen=True)
class PromoOverview:
    total_activations: int
    recent_promos: tuple[PromoCodeInfo, ...]


@dataclass(slots=True, frozen=True)
class PromoActivationResult:
    status: PromoActivationStatus
    promo: PromoCodeInfo | None
    message: str
