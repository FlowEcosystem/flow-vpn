from typing import Protocol
from uuid import UUID

from src.application.promos.dto import PromoCodeInfo


class PromoCodesRepository(Protocol):
    async def get_active_by_code(self, code: str) -> PromoCodeInfo | None: ...

    async def list_recent_active(self, limit: int) -> tuple[PromoCodeInfo, ...]: ...


class PromoRedemptionsRepository(Protocol):
    async def count_by_user_id(self, user_id: UUID) -> int: ...

    async def exists(self, *, promo_code: str, user_id: UUID) -> bool: ...

    async def create(self, *, promo_code: str, user_id: UUID) -> None: ...


class PromosUnitOfWork(Protocol):
    promo_codes: PromoCodesRepository
    promo_redemptions: PromoRedemptionsRepository

    async def __aenter__(self) -> "PromosUnitOfWork": ...

    async def __aexit__(self, exc_type: object, exc: BaseException | None, tb: object) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
