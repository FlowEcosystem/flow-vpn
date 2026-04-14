from typing import Protocol
from uuid import UUID

from src.application.users import UserProfile
from src.application.vpn.dto import (
    NewVpnAccessData,
    NewVpnAccessEventData,
    ProvisionedVpnAccess,
    UpdateVpnAccessData,
    VpnAccess,
    VpnAccessEvent,
)


class VpnAccessRepository(Protocol):
    async def get_by_id(self, access_id: UUID) -> VpnAccess | None: ...

    async def get_by_user_id(self, user_id: UUID) -> VpnAccess | None: ...

    async def list_by_user_id(self, user_id: UUID) -> tuple[VpnAccess, ...]: ...

    async def create(self, data: NewVpnAccessData) -> VpnAccess: ...

    async def update(self, access_id: UUID, data: UpdateVpnAccessData) -> VpnAccess: ...

    async def delete(self, access_id: UUID) -> None: ...

    async def list_active_expired(self) -> tuple[VpnAccess, ...]: ...


class VpnAccessEventRepository(Protocol):
    async def create(self, data: NewVpnAccessEventData) -> VpnAccessEvent: ...

    async def list_by_user_id(self, user_id: UUID, limit: int) -> tuple[VpnAccessEvent, ...]: ...


class VpnAccessUnitOfWork(Protocol):
    vpn_accesses: VpnAccessRepository
    vpn_access_events: VpnAccessEventRepository

    async def __aenter__(self) -> "VpnAccessUnitOfWork": ...

    async def __aexit__(self, exc_type: object, exc: BaseException | None, tb: object) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...


class VpnProvisioningGateway(Protocol):
    async def provision_vless_access(
        self,
        user: UserProfile,
        subscription_number: int,
    ) -> ProvisionedVpnAccess: ...

    async def enable_vless_access(self, external_username: str) -> ProvisionedVpnAccess: ...

    async def disable_vless_access(self, external_username: str) -> ProvisionedVpnAccess: ...

    async def extend_vless_access(
        self, external_username: str, bonus_days: int
    ) -> ProvisionedVpnAccess: ...

    async def make_vless_access_infinite(self, external_username: str) -> ProvisionedVpnAccess: ...

    async def reissue_vless_access(self, external_username: str) -> ProvisionedVpnAccess: ...

    async def delete_vless_access(self, external_username: str) -> None: ...
