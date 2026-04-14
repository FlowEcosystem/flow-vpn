from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from src.application.runtime import AccessMode
from src.application.users import UserProfile, UserSummary
from src.application.vpn import VpnAccess, VpnAccessEvent


@dataclass(slots=True, frozen=True)
class AdminDashboard:
    access_mode: AccessMode
    max_vpn_accesses_per_user: int
    total_users: int
    new_users_today: int
    premium_users: int


class AdminUsersFilter(StrEnum):
    ALL = "all"
    WITH_ACCESS = "with_access"
    WITHOUT_ACCESS = "without_access"


@dataclass(slots=True, frozen=True)
class AdminBulkOperationInfo:
    id: UUID
    admin_telegram_id: int
    action: str
    source_operation_id: UUID | None
    target_segment: str
    source_page: int
    is_global: bool
    status: str
    total_users: int
    processed_users: int
    affected_accesses: int
    skipped_users: int
    failed_users: int
    last_error: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


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
    vpn_accesses: tuple[VpnAccess, ...]
    history: tuple[VpnAccessEvent, ...]

    @property
    def vpn_access(self) -> VpnAccess | None:
        for access in reversed(self.vpn_accesses):
            if access.status == "active":
                return access
        return self.vpn_accesses[-1] if self.vpn_accesses else None
