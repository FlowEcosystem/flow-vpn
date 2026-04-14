"""Admin support router composition."""

from aiogram import Router

from .support_actions import router as admin_support_actions_router
from .support_list import router as admin_support_list_router
from .support_reply import router as admin_support_reply_router

router = Router(name="admin_support")
router.include_router(admin_support_list_router)
router.include_router(admin_support_reply_router)
router.include_router(admin_support_actions_router)

__all__ = ["router"]
