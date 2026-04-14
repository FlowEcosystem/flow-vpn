from src.application.users import UserProfile, UserSummary
from src.infrastructure.database.models import User


def map_user_profile(user: User) -> UserProfile:
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


def map_user_summary(user: User, has_vpn_access: bool) -> UserSummary:
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
