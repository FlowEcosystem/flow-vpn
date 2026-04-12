from src.application.users.dto import TelegramUserData
from src.application.users.ports import UsersUnitOfWork


class RegisterTelegramUserUseCase:
    def __init__(self, uow: UsersUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, data: TelegramUserData, *, referral_code: str | None = None) -> bool:
        async with self._uow:
            if await self._uow.users.exists_by_telegram_id(data.telegram_id):
                return False

            referred_by_user_id = None
            normalized_referral_code = (referral_code or "").strip().lower()
            if normalized_referral_code:
                referrer = await self._uow.users.get_by_referral_code(normalized_referral_code)
                if referrer is not None and referrer.telegram_id != data.telegram_id:
                    referred_by_user_id = referrer.id

            await self._uow.users.create(
                data,
                referred_by_user_id=referred_by_user_id,
            )
            await self._uow.commit()
            return True
