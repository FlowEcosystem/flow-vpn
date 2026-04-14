from src.application.promos.dto import EligibleVpnAccess, PromoCodeInfo
from src.application.vpn.dto import VpnAccess


def get_eligible_accesses(accesses: list[VpnAccess]) -> list[VpnAccess]:
    """Активные подписки с конечным сроком."""
    return [a for a in accesses if a.status == "active" and a.expires_at is not None]


def number_eligible_accesses(
    all_accesses: list[VpnAccess],
    eligible: list[VpnAccess],
) -> tuple[EligibleVpnAccess, ...]:
    sorted_all = sorted(all_accesses, key=lambda a: a.created_at)
    numbers = {a.id: i + 1 for i, a in enumerate(sorted_all)}
    sorted_eligible = sorted(eligible, key=lambda a: numbers[a.id])
    return tuple(
        EligibleVpnAccess(
            access_id=a.id,
            number=numbers[a.id],
            expires_at=a.expires_at,  # type: ignore[arg-type]
        )
        for a in sorted_eligible
    )


def promo_has_effect(promo: PromoCodeInfo) -> bool:
    return promo.bonus_days > 0 or promo.is_infinite
