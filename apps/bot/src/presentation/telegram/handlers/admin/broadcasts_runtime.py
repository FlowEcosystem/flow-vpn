# ruff: noqa: RUF001

import asyncio
import uuid as uuid_module
from datetime import UTC, datetime

import structlog
from aiogram.types import Message
from sqlalchemy import update

from src.infrastructure.database import Database
from src.infrastructure.database.models.broadcast import Broadcast as BroadcastModel

logger = structlog.get_logger(__name__)


async def run_broadcast_task(
    *,
    broadcast_id: uuid_module.UUID,
    text: str,
    telegram_ids: tuple[int, ...],
    bot,
    database: Database,
) -> None:
    sent = 0
    failed = 0
    total = len(telegram_ids)
    log = logger.bind(broadcast_id=str(broadcast_id), total=total)
    for tid in telegram_ids:
        try:
            await bot.send_message(tid, text, parse_mode="HTML")
            sent += 1
        except Exception as exc:
            failed += 1
            log.warning(
                "broadcast_message_failed",
                telegram_id=tid,
                error=str(exc),
            )
        await asyncio.sleep(0.05)

    log.info("broadcast_loop_finished", sent=sent, failed=failed)

    try:
        async with database.session_factory() as session:
            await session.execute(
                update(BroadcastModel)
                .where(BroadcastModel.id == broadcast_id)
                .values(
                    status="done",
                    sent_count=sent,
                    failed_count=failed,
                    completed_at=datetime.now(UTC),
                )
            )
            await session.commit()
    except Exception:
        logger.exception("broadcast_stats_update_failed", broadcast_id=str(broadcast_id))


def spawn_broadcast_task(
    *,
    summary_id: uuid_module.UUID,
    text: str,
    telegram_ids: tuple[int, ...],
    message: Message,
    database: Database,
) -> None:
    task = asyncio.create_task(
        run_broadcast_task(
            broadcast_id=summary_id,
            text=text,
            telegram_ids=telegram_ids,
            bot=message.bot,
            database=database,
        )
    )
    task.add_done_callback(lambda t: t.exception() if not t.cancelled() else None)
