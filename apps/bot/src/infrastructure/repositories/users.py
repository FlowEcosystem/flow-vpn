from datetime import datetime
from uuid import UUID

from sqlalchemy import String, cast, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.users import TelegramUserData, UserProfile, UserSummary
from src.infrastructure.database.models import User
from src.infrastructure.database.models import VpnAccess as VpnAccessModel


class SqlAlchemyUsersRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists_by_telegram_id(self, telegram_id: int) -> bool:
        stmt = select(User.id).where(User.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_telegram_id(self, telegram_id: int) -> UserProfile | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None

        return self._map_profile(user)

    async def get_by_referral_code(self, referral_code: str) -> UserProfile | None:
        stmt = select(User).where(User.referral_code == referral_code)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None

        return self._map_profile(user)

    async def count_referrals(self, user_id: UUID) -> int:
        stmt = select(func.count()).select_from(User).where(User.referred_by_user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def list_recent_referrals(self, user_id: UUID, limit: int) -> tuple[UserProfile, ...]:
        stmt = (
            select(User)
            .where(User.referred_by_user_id == user_id)
            .order_by(User.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return tuple(self._map_profile(user) for user in result.scalars().all())

    async def create(
        self,
        data: TelegramUserData,
        *,
        referred_by_user_id: UUID | None = None,
    ) -> None:
        user = User(
            telegram_id=data.telegram_id,
            referral_code=self._build_referral_code(data.telegram_id),
            referred_by_user_id=referred_by_user_id,
            username=data.username,
            first_name=data.first_name,
            last_name=data.last_name,
            language_code=data.language_code,
            is_bot=data.is_bot,
            is_premium=data.is_premium,
        )
        self._session.add(user)
        await self._session.flush()

    def _map_profile(self, user: User) -> UserProfile:
        return UserProfile(
            id=user.id,
            telegram_id=user.telegram_id,
            referral_code=user.referral_code,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code,
            is_premium=user.is_premium,
            created_at=user.created_at,
        )

    async def list_page(
        self,
        *,
        limit: int,
        offset: int,
        has_vpn_access: bool | None,
    ) -> tuple[UserSummary, ...]:
        has_vpn_access_expr = self._has_vpn_access_expr()
        stmt = (
            select(User, has_vpn_access_expr)
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if has_vpn_access is True:
            stmt = stmt.where(self._has_vpn_access_expr())
        elif has_vpn_access is False:
            stmt = stmt.where(~self._has_vpn_access_expr())
        result = await self._session.execute(stmt)
        rows = result.all()
        return tuple(self._map_summary(user, has_access) for user, has_access in rows)

    async def search(self, query: str, limit: int) -> tuple[UserSummary, ...]:
        normalized_query = query.strip()
        username_query = normalized_query.removeprefix("@")
        has_vpn_access = self._has_vpn_access_expr()

        filters = []
        if normalized_query.isdigit():
            filters.extend(
                [
                    User.telegram_id == int(normalized_query),
                    cast(User.telegram_id, String).ilike(f"%{normalized_query}%"),
                ]
            )

        if username_query:
            pattern = f"%{username_query}%"
            filters.extend(
                [
                    User.username.ilike(pattern),
                    User.first_name.ilike(pattern),
                    User.last_name.ilike(pattern),
                ]
            )

        if not filters:
            return ()

        stmt = (
            select(User, has_vpn_access)
            .where(or_(*filters))
            .order_by(User.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        return tuple(self._map_summary(user, has_access) for user, has_access in rows)

    async def count_all(self) -> int:
        stmt = select(func.count()).select_from(User)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_filtered(self, *, has_vpn_access: bool | None) -> int:
        stmt = select(func.count()).select_from(User)
        if has_vpn_access is True:
            stmt = stmt.where(self._has_vpn_access_expr())
        elif has_vpn_access is False:
            stmt = stmt.where(~self._has_vpn_access_expr())
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_with_vpn_access(self) -> int:
        stmt = select(func.count()).select_from(VpnAccessModel)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_created_since(self, created_from: datetime) -> int:
        stmt = select(func.count()).select_from(User).where(User.created_at >= created_from)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_premium(self) -> int:
        stmt = select(func.count()).select_from(User).where(User.is_premium.is_(True))
        result = await self._session.execute(stmt)
        return result.scalar_one()

    def _has_vpn_access_expr(self):
        return exists(
            select(VpnAccessModel.id).where(VpnAccessModel.user_id == User.id)
        ).label("has_vpn_access")

    def _build_referral_code(self, telegram_id: int) -> str:
        return f"u{telegram_id}"

    def _map_summary(self, user: User, has_vpn_access: bool) -> UserSummary:
        return UserSummary(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_premium=user.is_premium,
            created_at=user.created_at,
            has_vpn_access=has_vpn_access,
        )
