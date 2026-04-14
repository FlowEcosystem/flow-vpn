import math
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True, frozen=True)
class TariffInfo:
    id: UUID
    name: str
    duration_days: int
    price_rub: int
    is_active: bool
    sort_order: int

    def stars_amount(self, stars_rub_rate: float) -> int:
        """Количество Stars для оплаты (автоконвертация из рублей)."""
        return math.ceil(self.price_rub / stars_rub_rate)


@dataclass(slots=True, frozen=True)
class UpdateTariffData:
    name: str
    duration_days: int
    price_rub: int
    is_active: bool
    sort_order: int


@dataclass(slots=True, frozen=True)
class NewTariffData:
    name: str
    duration_days: int
    price_rub: int
    sort_order: int = 0


@dataclass(slots=True, frozen=True)
class PaymentInfo:
    id: UUID
    user_id: UUID
    tariff_id: UUID | None
    access_id: UUID | None
    amount_rub: int
    stars_amount: int | None
    provider: str  # yookassa | stars
    status: str   # pending | completed | failed | cancelled
    external_id: str | None
    payment_url: str | None
    created_at: datetime
    completed_at: datetime | None

    @property
    def is_pending(self) -> bool:
        return self.status == "pending"

    @property
    def is_completed(self) -> bool:
        return self.status == "completed"


@dataclass(slots=True, frozen=True)
class CreatedPayment:
    """Результат создания платежа в шлюзе YooKassa."""
    external_id: str
    payment_url: str


@dataclass(slots=True, frozen=True)
class NewPaymentData:
    user_id: UUID
    tariff_id: UUID
    access_id: UUID | None
    amount_rub: int
    stars_amount: int | None
    provider: str
    external_id: str | None = None
    payment_url: str | None = None
