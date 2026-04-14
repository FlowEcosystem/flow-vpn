import asyncio

import structlog
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka
from redis.asyncio import Redis

from src.app.config import Settings
from src.app.container import create_container
from src.app.logging import setup_logging
from src.application.vpn import VpnService
from src.infrastructure.database import Database
from src.presentation.telegram.handlers.admin import run_admin_bulk_operations_loop
from src.presentation.telegram import router

logger = structlog.get_logger(__name__)

_EXPIRE_INTERVAL_SECONDS = 10 * 60  # 10 minutes


async def _run_expire_loop(container: AsyncContainer) -> None:
    while True:
        await asyncio.sleep(_EXPIRE_INTERVAL_SECONDS)
        try:
            async with container() as request_container:
                vpn = await request_container.get(VpnService)
                count = await vpn.expire_accesses()
                if count:
                    logger.info("expire_loop_ran", expired_count=count)
        except Exception:
            logger.exception("expire_loop_error")


async def main() -> None:
    settings = Settings()
    setup_logging(json_logs=settings.log_json)

    database = Database()
    database.setup(settings)
    container = create_container(settings=settings, database=database)
    redis = await container.get(Redis)

    session = AiohttpSession(proxy=settings.bot_proxy) if settings.bot_proxy else None
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )
    dispatcher = Dispatcher()
    dispatcher["settings"] = settings
    dispatcher["redis"] = redis

    dispatcher.include_router(router)
    setup_dishka(container=container, router=dispatcher, auto_inject=True)
    dispatcher.shutdown.register(container.close)

    expire_task = asyncio.create_task(_run_expire_loop(container))
    admin_bulk_task = asyncio.create_task(
        run_admin_bulk_operations_loop(
            container=container,
            bot=bot,
            database=database,
        )
    )

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot)
    finally:
        expire_task.cancel()
        admin_bulk_task.cancel()
        await asyncio.gather(expire_task, admin_bulk_task, return_exceptions=True)
        await bot.session.close()
        await redis.aclose()
        await database.dispose()


if __name__ == "__main__":
    asyncio.run(main())
