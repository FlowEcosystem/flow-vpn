from datetime import UTC, datetime

import httpx

from src.app.config import Settings
from src.application.status import ServiceStatusGateway, ServiceStatusLevel, ServiceStatusOverview


class MarzbanServiceStatusGateway(ServiceStatusGateway):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_status(self) -> ServiceStatusOverview:
        if not self._settings.marzban_is_configured:
            return ServiceStatusOverview(
                level=ServiceStatusLevel.DEGRADED,
                checked_at=datetime.now(UTC),
            )

        try:
            async with httpx.AsyncClient(
                base_url=self._settings.marzban_base_url,
                timeout=10.0,
            ) as client:
                response = await client.post(
                    "/api/admin/token",
                    data={
                        "username": self._settings.marzban_username,
                        "password": self._settings.marzban_password,
                    },
                )
                response.raise_for_status()
        except httpx.HTTPError:
            level = ServiceStatusLevel.DEGRADED
        else:
            level = ServiceStatusLevel.ONLINE

        return ServiceStatusOverview(
            level=level,
            checked_at=datetime.now(UTC),
        )
