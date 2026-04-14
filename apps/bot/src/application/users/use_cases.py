import structlog

from src.application.users.dto import TelegramUserData
from src.application.users.ports import UsersUnitOfWork

logger = structlog.get_logger(__name__)


class UsersService:
    def __init__(self, uow: UsersUnitOfWork) -> None:
        self._uow = uow

    async def register(self, data: TelegramUserData, *, referral_code: str | None = None) -> bool:
        async with self._uow:
            normalized_referral_code = (referral_code or "").strip().lower()
            existing_user = await self._uow.users.get_by_telegram_id(data.telegram_id)
            referred_by_user_id = None

            referrer = None
            if normalized_referral_code:
                candidate = await self._uow.users.get_by_referral_code(normalized_referral_code)
                if candidate is not None and candidate.telegram_id != data.telegram_id:
                    referrer = candidate
                    referred_by_user_id = candidate.id

            if existing_user is not None:
                if referred_by_user_id is not None:
                    is_attached = await self._uow.users.attach_referrer_if_eligible(
                        existing_user.id,
                        referred_by_user_id=referred_by_user_id,
                    )
                    if is_attached:
                        await self._uow.commit()
                        logger.info(
                            "referral_attached",
                            telegram_id=data.telegram_id,
                            referred_by=referrer.telegram_id if referrer else None,
                        )
                return False

            await self._uow.users.create(
                data,
                referred_by_user_id=referred_by_user_id,
            )
            await self._uow.commit()
            logger.info(
                "user_registered",
                telegram_id=data.telegram_id,
                username=data.username,
                referred_by=referrer.telegram_id if referrer else None,
            )
            return True
