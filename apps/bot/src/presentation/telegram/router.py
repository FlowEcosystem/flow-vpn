from aiogram import Router

from src.presentation.telegram.handlers.admin import router as admin_router
from src.presentation.telegram.handlers.client import router as client_router
from src.presentation.telegram.handlers.start import router as start_router

router = Router(name="telegram")
router.include_router(start_router)
router.include_router(client_router)
router.include_router(admin_router)

__all__ = ["router"]
