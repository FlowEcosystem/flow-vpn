from src.application.referrals.dto import ReferralInvitee, ReferralOverview
from src.application.users import UsersUnitOfWork


class ReferralsService:
    def __init__(self, users_uow: UsersUnitOfWork) -> None:
        self._users_uow = users_uow

    async def get_overview(self, telegram_id: int, *, limit: int = 5) -> ReferralOverview | None:
        async with self._users_uow:
            user = await self._users_uow.users.get_by_telegram_id(telegram_id)
            if user is None:
                return None

            total_referrals = await self._users_uow.users.count_referrals(user.id)
            activated_referrals = await self._users_uow.users.count_referrals(
                user.id,
                activated_only=True,
            )
            recent_referrals = await self._users_uow.users.list_recent_referrals(user.id, limit)

        return ReferralOverview(
            referral_code=user.referral_code,
            activated_referrals=activated_referrals,
            pending_referrals=max(0, total_referrals - activated_referrals),
            recent_referrals=tuple(
                ReferralInvitee(
                    first_name=invitee.first_name,
                    username=invitee.username,
                    created_at=invitee.created_at,
                    has_activated_vpn=invitee.has_vpn_access,
                )
                for invitee in recent_referrals
            ),
        )
