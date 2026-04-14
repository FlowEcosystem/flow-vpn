import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class BroadcastSummary:
    id: uuid.UUID
    target_segment: str
    status: str
    total_count: int
    sent_count: int
    failed_count: int
    created_at: datetime
    completed_at: datetime | None
