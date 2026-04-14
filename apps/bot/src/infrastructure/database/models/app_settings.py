from datetime import datetime

from sqlalchemy import DateTime, Enum, SmallInteger, func
from sqlalchemy.orm import Mapped, mapped_column

from src.application.runtime import AccessMode
from src.infrastructure.database.base import Base


class AppSettings(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, default=1)
    access_mode: Mapped[AccessMode] = mapped_column(
        Enum(
            AccessMode,
            name="access_mode",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=AccessMode.FREE_ACCESS,
    )
    max_vpn_accesses_per_user: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
