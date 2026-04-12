from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class ReferralInvitee:
    first_name: str | None
    username: str | None
    created_at: datetime


@dataclass(slots=True, frozen=True)
class ReferralOverview:
    referral_code: str
    total_referrals: int
    recent_referrals: tuple[ReferralInvitee, ...]
