# ruff: noqa: RUF001

from .promos_create import (
    build_admin_promo_create_bonus_text,
    build_admin_promo_create_code_text,
    build_admin_promo_create_limit_text,
    build_admin_promo_create_scope_text,
    build_admin_promo_create_title_text,
    build_admin_promo_create_type_text,
)
from .promos_list import build_admin_promo_detail_text, build_admin_promos_list_text

__all__ = [
    "build_admin_promo_create_bonus_text",
    "build_admin_promo_create_code_text",
    "build_admin_promo_create_limit_text",
    "build_admin_promo_create_scope_text",
    "build_admin_promo_create_title_text",
    "build_admin_promo_create_type_text",
    "build_admin_promo_detail_text",
    "build_admin_promos_list_text",
]
