"""Admin broadcasts router composition."""

from aiogram import Router

from .broadcasts_create import router as admin_broadcasts_create_router
from .broadcasts_list import router as admin_broadcasts_list_router

router = Router(name="admin_broadcasts")
router.include_router(admin_broadcasts_list_router)
router.include_router(admin_broadcasts_create_router)

__all__ = ["router"]
