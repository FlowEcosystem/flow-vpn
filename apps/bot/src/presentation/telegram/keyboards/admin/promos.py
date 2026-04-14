# ruff: noqa: RUF001

from .promos_create import (
    build_admin_promo_create_cancel_menu,
    build_admin_promo_scope_menu,
    build_admin_promo_type_menu,
)
from .promos_list import build_admin_promo_detail_menu, build_admin_promos_list_menu

__all__ = [
    "build_admin_promo_create_cancel_menu",
    "build_admin_promo_detail_menu",
    "build_admin_promo_scope_menu",
    "build_admin_promo_type_menu",
    "build_admin_promos_list_menu",
]
