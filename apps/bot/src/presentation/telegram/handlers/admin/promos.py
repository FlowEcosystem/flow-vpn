"""Admin promos router composition."""

from aiogram import Router

from .promos_actions import router as admin_promos_actions_router
from .promos_create import router as admin_promos_create_router
from .promos_list import router as admin_promos_list_router

router = Router(name="admin_promos")
router.include_router(admin_promos_list_router)
router.include_router(admin_promos_actions_router)
router.include_router(admin_promos_create_router)

__all__ = ["router"]
