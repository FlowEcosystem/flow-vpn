"""Admin router composition and bulk worker export."""

from aiogram import Router

from .broadcasts import router as admin_broadcasts_router
from .bulk import run_admin_bulk_operations_loop
from .home import router as admin_home_router
from .promos import router as admin_promos_router
from .support import router as admin_support_router
from .users import router as admin_users_router
from .users_bulk import router as admin_users_bulk_router

router = Router(name="admin")
router.include_router(admin_home_router)
router.include_router(admin_users_router)
router.include_router(admin_users_bulk_router)
router.include_router(admin_promos_router)
router.include_router(admin_support_router)
router.include_router(admin_broadcasts_router)

__all__ = ["router", "run_admin_bulk_operations_loop"]
