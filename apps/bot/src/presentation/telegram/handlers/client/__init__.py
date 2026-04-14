"""Client router composition."""

from aiogram import Router

from .promos import router as promos_router
from .referrals import router as referrals_router
from .reviews import router as reviews_router
from .status import router as status_router
from .support import router as support_router

router = Router(name="client")
router.include_router(referrals_router)
router.include_router(promos_router)
router.include_router(reviews_router)
router.include_router(status_router)
router.include_router(support_router)

__all__ = ["router"]
