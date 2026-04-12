from src.application.status.dto import ServiceStatusOverview
from src.application.status.ports import ServiceStatusGateway


class GetServiceStatusUseCase:
    def __init__(self, gateway: ServiceStatusGateway) -> None:
        self._gateway = gateway

    async def execute(self) -> ServiceStatusOverview:
        return await self._gateway.get_status()
