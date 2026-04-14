from aiogram import Router

from src.presentation.telegram.handlers.admin import router as admin_router
from src.presentation.telegram.handlers.client import router as client_router
from src.presentation.telegram.handlers.errors import router as errors_router
from src.presentation.telegram.handlers.start import router as start_router
from src.presentation.telegram.middleware import RateLimitMiddleware, UserLoggingMiddleware

router = Router(name="telegram")

# Order matters: logging → rate limiting → handler
_logging = UserLoggingMiddleware()
_rate_limit = RateLimitMiddleware()
for observer in (router.message, router.callback_query):
    observer.outer_middleware(_logging)
    observer.outer_middleware(_rate_limit)

router.include_router(errors_router)
router.include_router(start_router)
router.include_router(client_router)
router.include_router(admin_router)

__all__ = ["router"]
