from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class ReferralInvitee:
    first_name: str | None
    username: str | None
    created_at: datetime
    has_activated_vpn: bool


@dataclass(slots=True, frozen=True)
class ReferralOverview:
    referral_code: str
    activated_referrals: int
    pending_referrals: int
    recent_referrals: tuple[ReferralInvitee, ...]
