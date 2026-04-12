from dataclasses import dataclass
from enum import StrEnum

from src.application.runtime import AccessMode
from src.application.users import UserProfile, UserSummary
from src.application.vpn import VpnAccess, VpnAccessEvent


@dataclass(slots=True, frozen=True)
class AdminDashboard:
    access_mode: AccessMode
    total_users: int
    new_users_today: int
    premium_users: int


class AdminUsersFilter(StrEnum):
    ALL = "all"
    WITH_ACCESS = "with_access"
    WITHOUT_ACCESS = "without_access"


@dataclass(slots=True, frozen=True)
class AdminUsersOverview:
    total_users: int
    users_with_access: int
    total_filtered: int
    current_page: int
    has_next_page: bool
    current_filter: AdminUsersFilter
    recent_users: tuple[UserSummary, ...]


@dataclass(slots=True, frozen=True)
class AdminUserSearchResult:
    query: str
    users: tuple[UserSummary, ...]


@dataclass(slots=True, frozen=True)
class AdminUserDetail:
    user: UserProfile
    vpn_access: VpnAccess | None
    history: tuple[VpnAccessEvent, ...]
