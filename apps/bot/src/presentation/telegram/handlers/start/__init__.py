"""Start router composition."""

from aiogram import Router

from .account import router as account_router
from .buy import router as buy_router
from .common import extract_referral_code, safe_edit_message
from .home import router as home_router

router = Router(name="start")
router.include_router(home_router)
router.include_router(buy_router)
router.include_router(account_router)

__all__ = ["extract_referral_code", "router", "safe_edit_message"]
