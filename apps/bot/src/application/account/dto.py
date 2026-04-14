from dataclasses import dataclass
from datetime import datetime

from src.application.runtime import AccessMode
from src.application.vpn import VpnAccess


@dataclass(slots=True, frozen=True)
class TelegramAccountOverview:
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    language_code: str | None
    is_premium: bool | None
    created_at: datetime
    access_mode: AccessMode
    vpn_accesses: tuple[VpnAccess, ...]
