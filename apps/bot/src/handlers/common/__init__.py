from aiogram import Router

from .echo import router as echo_router
from .start import router as start_router

router = Router(name="common")
router.include_router(start_router)
router.include_router(echo_router)

__all__ = ["router"]
