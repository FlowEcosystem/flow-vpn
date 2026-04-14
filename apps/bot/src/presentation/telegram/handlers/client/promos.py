"""Client promos router composition."""

from aiogram import Router

from .promos_apply import router as client_promos_apply_router
from .promos_section import router as client_promos_section_router

router = Router(name="client_promos")
router.include_router(client_promos_section_router)
router.include_router(client_promos_apply_router)

__all__ = ["router"]
