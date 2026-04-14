import re
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, cast, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.users import TelegramUserData, UserProfile, UserSummary
from src.infrastructure.database.models import User
from src.infrastructure.database.models import VpnAccess as VpnAccessModel
from src.infrastructure.repositories.users.mappers import map_user_profile, map_user_summary
from src.infrastructure.repositories.users.queries import has_vpn_access_expr


class SqlAlchemyUsersRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists_by_telegram_id(self, telegram_id: int) -> bool:
        stmt = select(User.id).where(User.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_id(self, user_id: UUID) -> UserProfile | None:
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return map_user_profile(user)

    async def get_by_telegram_id(self, telegram_id: int) -> UserProfile | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return map_user_profile(user)

    async def get_by_referral_code(self, referral_code: str) -> UserProfile | None:
        stmt = select(User).where(User.referral_code == referral_code)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return map_user_profile(user)

    async def count_referrals(self, user_id: UUID, *, activated_only: bool = False) -> int:
        stmt = select(func.count()).select_from(User).where(User.referred_by_user_id == user_id)
        if activated_only:
            stmt = stmt.where(has_vpn_access_expr())
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def list_recent_referrals(self, user_id: UUID, limit: int) -> tuple[UserSummary, ...]:
        has_vpn_access = has_vpn_access_expr().label("has_vpn_access")
        stmt = (
            select(User, has_vpn_access)
            .where(User.referred_by_user_id == user_id)
            .order_by(User.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        return tuple(map_user_summary(user, has_access) for user, has_access in rows)

    async def attach_referrer_if_eligible(
        self,
        user_id: UUID,
        *,
        referred_by_user_id: UUID,
    ) -> bool:
        stmt = (
            update(User)
            .where(
                User.id == user_id,
                User.id != referred_by_user_id,
                User.referred_by_user_id.is_(None),
                ~has_vpn_access_expr(),
            )
            .values(referred_by_user_id=referred_by_user_id)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return (result.rowcount or 0) > 0

    async def create(
        self,
        data: TelegramUserData,
        *,
        referred_by_user_id: UUID | None = None,
    ) -> None:
        user = User(
            telegram_id=data.telegram_id,
            referral_code=self._build_referral_code(data),
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

    async def list_telegram_ids(self, *, has_vpn_access: bool | None) -> tuple[int, ...]:
        stmt = select(User.telegram_id)
        if has_vpn_access is True:
            stmt = stmt.where(has_vpn_access_expr())
        elif has_vpn_access is False:
            stmt = stmt.where(~has_vpn_access_expr())
        result = await self._session.execute(stmt)
        return tuple(result.scalars().all())

    async def list_page(
        self,
        *,
        limit: int,
        offset: int,
        has_vpn_access: bool | None,
    ) -> tuple[UserSummary, ...]:
        has_vpn_access_flag = has_vpn_access_expr()
        stmt = (
            select(User, has_vpn_access_flag)
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if has_vpn_access is True:
            stmt = stmt.where(has_vpn_access_expr())
        elif has_vpn_access is False:
            stmt = stmt.where(~has_vpn_access_expr())
        result = await self._session.execute(stmt)
        rows = result.all()
        return tuple(map_user_summary(user, has_access) for user, has_access in rows)

    async def search(self, query: str, limit: int) -> tuple[UserSummary, ...]:
        normalized_query = query.strip()
        username_query = normalized_query.removeprefix("@")
        has_vpn_access = has_vpn_access_expr()

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
        return tuple(map_user_summary(user, has_access) for user, has_access in rows)

    async def count_all(self) -> int:
        stmt = select(func.count()).select_from(User)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_filtered(self, *, has_vpn_access: bool | None) -> int:
        stmt = select(func.count()).select_from(User)
        if has_vpn_access is True:
            stmt = stmt.where(has_vpn_access_expr())
        elif has_vpn_access is False:
            stmt = stmt.where(~has_vpn_access_expr())
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_with_vpn_access(self) -> int:
        stmt = select(func.count(func.distinct(VpnAccessModel.user_id))).select_from(VpnAccessModel)
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

    def _build_referral_code(self, data: TelegramUserData) -> str:
        base_source = (data.username or f"u{data.telegram_id}").strip().lower().removeprefix("@")
        normalized = re.sub(r"[^a-z0-9]+", "", base_source)[:16]
        prefix = normalized or "flow"
        return f"{prefix}{uuid4().hex[:8]}"
