# ruff: noqa: RUF001

import asyncio
from time import monotonic
from uuid import UUID

import structlog
from aiogram import Bot

from src.application.admin import AdminBulkOperationsService, AdminService
from src.infrastructure.database import Database

from .bulk_rendering import render_admin_bulk_operation_message

logger = structlog.get_logger(__name__)

BULK_PROGRESS_UPDATE_INTERVAL = 0.75
BULK_PROGRESS_UPDATE_EVERY = 5
ADMIN_BULK_WORKER_POLL_INTERVAL_SECONDS = 2


async def execute_admin_bulk_operation_for_user(
    *,
    container,
    admin_bulk: AdminBulkOperationsService,
    current_operation_id: UUID,
    source_operation_id: UUID | None,
    action: str,
    telegram_id: int,
    admin_telegram_id: int,
) -> tuple[int, bool]:
    async with container() as request_container:
        admin = await request_container.get(AdminService)
        return await admin_bulk.execute_operation_for_user(
            admin=admin,
            current_operation_id=current_operation_id,
            source_operation_id=source_operation_id,
            action=action,
            telegram_id=telegram_id,
            admin_telegram_id=admin_telegram_id,
        )


async def run_admin_bulk_operation(
    *,
    container,
    bot: Bot,
    admin_bulk: AdminBulkOperationsService,
    operation_id: UUID,
) -> None:
    operation = await admin_bulk.get_operation(operation_id)
    if operation is None or operation.status in {"done", "failed", "cancelled"}:
        return

    await admin_bulk.set_operation_running(operation_id)
    operation = await admin_bulk.get_operation(operation_id)
    if operation is None:
        return

    await render_admin_bulk_operation_message(bot, operation)

    processed_users = operation.processed_users
    skipped_users = operation.skipped_users
    failed_users = operation.failed_users
    affected_accesses = operation.affected_accesses
    last_progress_update = 0.0

    try:
        for telegram_id in operation.target_telegram_ids[processed_users:]:
            if await admin_bulk.is_operation_cancelled(operation.id):
                break
            try:
                affected_for_user, ok = await execute_admin_bulk_operation_for_user(
                    container=container,
                    admin_bulk=admin_bulk,
                    current_operation_id=operation.id,
                    source_operation_id=operation.source_operation_id,
                    action=operation.action,
                    telegram_id=telegram_id,
                    admin_telegram_id=operation.admin_telegram_id,
                )
            except (RuntimeError, ValueError):
                failed_users += 1
            else:
                if not ok:
                    failed_users += 1
                else:
                    affected_accesses += affected_for_user
                    if affected_for_user == 0:
                        skipped_users += 1

            processed_users += 1
            if await admin_bulk.is_operation_cancelled(operation.id):
                break

            now = monotonic()
            if (
                processed_users % BULK_PROGRESS_UPDATE_EVERY == 0
                or processed_users == operation.total_users
                or (now - last_progress_update) >= BULK_PROGRESS_UPDATE_INTERVAL
            ):
                await admin_bulk.update_operation_progress(
                    operation_id=operation.id,
                    processed_users=processed_users,
                    affected_accesses=affected_accesses,
                    skipped_users=skipped_users,
                    failed_users=failed_users,
                )
                refreshed = await admin_bulk.get_operation(operation.id)
                if refreshed is not None:
                    await render_admin_bulk_operation_message(bot, refreshed)
                last_progress_update = now

        if await admin_bulk.is_operation_cancelled(operation.id):
            await admin_bulk.finalize_cancelled_operation(
                operation_id=operation.id,
                processed_users=processed_users,
                affected_accesses=affected_accesses,
                skipped_users=skipped_users,
                failed_users=failed_users,
            )
            final_operation = await admin_bulk.get_operation(operation.id)
            if final_operation is not None:
                await render_admin_bulk_operation_message(bot, final_operation)
            return

        await admin_bulk.complete_operation(
            operation_id=operation.id,
            processed_users=processed_users,
            affected_accesses=affected_accesses,
            skipped_users=skipped_users,
            failed_users=failed_users,
        )
    except Exception as exc:
        logger.exception("admin_bulk_operation_failed", operation_id=str(operation.id))
        await admin_bulk.fail_operation(
            operation_id=operation.id,
            processed_users=processed_users,
            affected_accesses=affected_accesses,
            skipped_users=skipped_users,
            failed_users=failed_users,
            error_message=str(exc),
        )

    final_operation = await admin_bulk.get_operation(operation.id)
    if final_operation is not None:
        await render_admin_bulk_operation_message(bot, final_operation)


async def run_admin_bulk_operations_loop(
    *,
    container,
    bot: Bot,
    database: Database,
) -> None:
    admin_bulk = AdminBulkOperationsService(database)
    while True:
        try:
            operation_id = await admin_bulk.get_next_operation_id()
            if operation_id is None:
                await asyncio.sleep(ADMIN_BULK_WORKER_POLL_INTERVAL_SECONDS)
                continue
            await run_admin_bulk_operation(
                container=container,
                bot=bot,
                admin_bulk=admin_bulk,
                operation_id=operation_id,
            )
        except Exception:
            logger.exception("admin_bulk_operations_loop_error")
            await asyncio.sleep(ADMIN_BULK_WORKER_POLL_INTERVAL_SECONDS)
