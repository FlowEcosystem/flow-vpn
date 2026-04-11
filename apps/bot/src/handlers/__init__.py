from aiogram import Router

from src.handlers.common import router as common_router

router = Router(name="root")
router.include_router(common_router)

__all__ = ["router"]
