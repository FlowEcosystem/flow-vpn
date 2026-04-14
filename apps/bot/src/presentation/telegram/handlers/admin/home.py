"""Admin home router composition."""

from aiogram import Router

from .home_access import router as admin_home_access_router
from .home_entry import router as admin_home_entry_router
from .home_sections import router as admin_home_sections_router

router = Router(name="admin_home")
router.include_router(admin_home_entry_router)
router.include_router(admin_home_access_router)
router.include_router(admin_home_sections_router)

__all__ = ["router"]
