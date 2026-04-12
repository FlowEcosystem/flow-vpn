from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class ServiceStatusLevel(StrEnum):
    ONLINE = "online"
    DEGRADED = "degraded"


@dataclass(slots=True, frozen=True)
class ServiceStatusOverview:
    level: ServiceStatusLevel
    checked_at: datetime
