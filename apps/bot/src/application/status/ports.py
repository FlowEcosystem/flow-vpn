from typing import Protocol

from src.application.status.dto import ServiceStatusOverview


class ServiceStatusGateway(Protocol):
    async def get_status(self) -> ServiceStatusOverview: ...
