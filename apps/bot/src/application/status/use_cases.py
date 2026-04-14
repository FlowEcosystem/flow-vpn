from src.application.status.dto import ServiceStatusOverview
from src.application.status.ports import ServiceStatusGateway


class StatusService:
    def __init__(self, gateway: ServiceStatusGateway) -> None:
        self._gateway = gateway

    async def get_status(self) -> ServiceStatusOverview:
        return await self._gateway.get_status()
