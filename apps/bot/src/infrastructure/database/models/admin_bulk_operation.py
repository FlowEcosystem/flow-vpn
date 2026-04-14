import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base import Base


class AdminBulkOperation(Base):
    __tablename__ = "admin_bulk_operations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    source_operation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    target_segment: Mapped[str] = mapped_column(String(32), nullable=False)
    source_page: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_global: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    total_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    affected_accesses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    target_telegram_ids: Mapped[list[int]] = mapped_column(JSONB, nullable=False)
    message_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
