from src.application.account.dto import TelegramAccountOverview
from src.application.runtime.ports import RuntimeSettingsUnitOfWork
from src.application.users.ports import UsersUnitOfWork
from src.application.vpn.ports import VpnAccessUnitOfWork


class GetTelegramAccountUseCase:
    def __init__(
        self,
        users_uow: UsersUnitOfWork,
        runtime_settings_uow: RuntimeSettingsUnitOfWork,
        vpn_access_uow: VpnAccessUnitOfWork,
    ) -> None:
        self._users_uow = users_uow
        self._runtime_settings_uow = runtime_settings_uow
        self._vpn_access_uow = vpn_access_uow

    async def execute(self, telegram_id: int) -> TelegramAccountOverview | None:
        async with self._users_uow:
            user = await self._users_uow.users.get_by_telegram_id(telegram_id)

        if user is None:
            return None

        async with self._runtime_settings_uow:
            access_mode = await self._runtime_settings_uow.settings.get_access_mode()

        async with self._vpn_access_uow:
            vpn_access = await self._vpn_access_uow.vpn_accesses.get_by_user_id(user.id)

        return TelegramAccountOverview(
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code,
            is_premium=user.is_premium,
            created_at=user.created_at,
            access_mode=access_mode,
            vpn_access=vpn_access,
        )
