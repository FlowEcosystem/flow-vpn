from sqlalchemy import exists, select

from src.infrastructure.database.models import User
from src.infrastructure.database.models import VpnAccess as VpnAccessModel


def has_vpn_access_expr():
    return exists(select(VpnAccessModel.id).where(VpnAccessModel.user_id == User.id))
