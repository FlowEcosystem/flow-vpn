import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class SupportOverview:
    support_url: str | None
    support_title: str
    closed_tickets_count: int
    average_support_rating: float | None
    total_support_ratings: int


@dataclass(slots=True, frozen=True)
class SupportTicketReplyItem:
    admin_telegram_id: int
    text: str
    created_at: datetime


@dataclass(slots=True, frozen=True)
class SupportTicketSummary:
    id: uuid.UUID
    user_telegram_id: int
    user_first_name: str | None
    user_username: str | None
    message: str
    status: str
    reply_count: int
    created_at: datetime


@dataclass(slots=True, frozen=True)
class SupportTicketDetail:
    id: uuid.UUID
    user_telegram_id: int
    user_first_name: str | None
    user_username: str | None
    message: str
    status: str
    replies: tuple[SupportTicketReplyItem, ...]
    created_at: datetime
