from src.application.vpn import VpnAccess
from src.infrastructure.database.models import VpnAccess as VpnAccessModel


def map_vpn_access(access: VpnAccessModel) -> VpnAccess:
    return VpnAccess(
        id=access.id,
        user_id=access.user_id,
        provider=access.provider,
        status=access.status,
        external_username=access.external_username,
        subscription_url=access.subscription_url,
        vless_links=tuple(access.vless_links),
        issued_at=access.issued_at,
        expires_at=access.expires_at,
        created_at=access.created_at,
        updated_at=access.updated_at,
    )
