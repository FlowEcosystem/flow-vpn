"""Admin users bulk router composition."""

from aiogram import Router

from .users_bulk_actions import router as admin_users_bulk_actions_router
from .users_bulk_history import router as admin_users_bulk_history_router
from .users_bulk_menu import router as admin_users_bulk_menu_router

router = Router(name="admin_users_bulk")
router.include_router(admin_users_bulk_menu_router)
router.include_router(admin_users_bulk_actions_router)
router.include_router(admin_users_bulk_history_router)

__all__ = ["router"]
