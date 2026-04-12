from src.application.referrals.dto import ReferralInvitee, ReferralOverview
from src.application.users import UsersUnitOfWork


class GetReferralOverviewUseCase:
    def __init__(self, users_uow: UsersUnitOfWork) -> None:
        self._users_uow = users_uow

    async def execute(self, telegram_id: int, *, limit: int = 5) -> ReferralOverview | None:
        async with self._users_uow:
            user = await self._users_uow.users.get_by_telegram_id(telegram_id)
            if user is None:
                return None

            total_referrals = await self._users_uow.users.count_referrals(user.id)
            recent_referrals = await self._users_uow.users.list_recent_referrals(user.id, limit)

        return ReferralOverview(
            referral_code=user.referral_code,
            total_referrals=total_referrals,
            recent_referrals=tuple(
                ReferralInvitee(
                    first_name=invitee.first_name,
                    username=invitee.username,
                    created_at=invitee.created_at,
                )
                for invitee in recent_referrals
            ),
        )
