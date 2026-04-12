from src.app.config import Settings
from src.application.support.dto import SupportOverview


class GetSupportOverviewUseCase:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def execute(self) -> SupportOverview:
        return SupportOverview(
            support_url=self._settings.support_url,
            support_title=self._settings.support_title,
        )
