"""Admin users router composition."""

from aiogram import Router

from .users_access_actions import router as admin_users_access_actions_router
from .users_detail import router as admin_users_detail_router
from .users_overview import router as admin_users_overview_router

router = Router(name="admin_users")
router.include_router(admin_users_overview_router)
router.include_router(admin_users_detail_router)
router.include_router(admin_users_access_actions_router)

__all__ = ["router"]
