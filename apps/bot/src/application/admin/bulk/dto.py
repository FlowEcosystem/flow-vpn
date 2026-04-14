from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

BULK_USERS_PAGE_SIZE = 50

ADMIN_BULK_ACTION_ISSUE = "issue"
ADMIN_BULK_ACTION_DISABLE = "disable"
ADMIN_BULK_ACTION_DELETE = "delete"
ADMIN_BULK_ACTION_ROLLBACK_ISSUE = "rollback_issue"
ADMIN_BULK_ACTION_ROLLBACK_DISABLE = "rollback_disable"


@dataclass(slots=True, frozen=True)
class AdminBulkOperationSnapshot:
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
    target_telegram_ids: tuple[int, ...]
    message_chat_id: int
    message_id: int
    last_error: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
