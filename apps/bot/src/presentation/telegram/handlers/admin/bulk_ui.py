# ruff: noqa: RUF001

import uuid as uuid_module
from datetime import UTC, datetime
from time import monotonic

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.app.config import Settings
from src.application.admin import (
    BULK_USERS_PAGE_SIZE,
    AdminBulkOperationSnapshot,
    AdminBulkOperationsService,
    AdminService,
)
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import (
    build_admin_users_bulk_progress_menu,
    build_admin_users_bulk_result_menu,
    build_admin_users_global_bulk_actions_menu,
)
from src.presentation.telegram.screens.admin import (
    build_admin_users_bulk_progress_text,
    build_admin_users_bulk_result_text,
    build_admin_users_global_bulk_actions_text,
)

from .bulk_rendering import build_admin_bulk_operation_menu, build_admin_bulk_operation_text
from .common import answer_access_denied, is_admin_user, parse_admin_users_scope

BULK_PROGRESS_UPDATE_INTERVAL = 0.75
BULK_PROGRESS_UPDATE_EVERY = 5


async def enqueue_admin_users_bulk_operation(
    *,
    callback: CallbackQuery,
    settings: Settings,
    state: FSMContext,
    admin: AdminService,
    admin_bulk: AdminBulkOperationsService,
    action_prefix: str,
    action: str,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    callback_data = callback.data
    message = callback.message
    if callback_data is None or not isinstance(message, Message):
        await callback.answer()
        return

    parsed = parse_admin_users_scope(callback_data, action_prefix)
    if parsed is None:
        await callback.answer("Не удалось определить сегмент.", show_alert=True)
        return

    current_filter, current_page = parsed
    overview = await admin.get_users_overview(
        page=current_page,
        current_filter=current_filter,
    )
    if overview.total_filtered == 0:
        await callback.answer("В этом сегменте нет пользователей.", show_alert=True)
        return

    target_telegram_ids = await admin_bulk.collect_target_telegram_ids(
        admin=admin,
        current_filter=current_filter,
    )
    if not target_telegram_ids:
        await callback.answer("В этом сегменте нет пользователей.", show_alert=True)
        return

    queued_operation = AdminBulkOperationSnapshot(
        id=uuid_module.uuid4(),
        admin_telegram_id=telegram_user.id,
        action=action,
        source_operation_id=None,
        target_segment=current_filter.value,
        source_page=current_page,
        is_global=True,
        status="pending",
        total_users=len(target_telegram_ids),
        processed_users=0,
        affected_accesses=0,
        skipped_users=0,
        failed_users=0,
        target_telegram_ids=tuple(target_telegram_ids),
        message_chat_id=0,
        message_id=0,
        last_error=None,
        created_at=datetime.now(UTC),
        started_at=None,
        completed_at=None,
    )
    status_message = await message.answer(
        build_admin_bulk_operation_text(queued_operation),
        reply_markup=build_admin_bulk_operation_menu(queued_operation),
    )

    await admin_bulk.enqueue_operation(
        operation_id=queued_operation.id,
        admin_telegram_id=telegram_user.id,
        action=action,
        source_operation_id=None,
        target_segment=current_filter.value,
        source_page=current_page,
        is_global=True,
        target_telegram_ids=tuple(target_telegram_ids),
        message_chat_id=status_message.chat.id,
        message_id=status_message.message_id,
    )

    await state.clear()
    await safe_edit_message(
        callback,
        text=build_admin_users_global_bulk_actions_text(overview),
        reply_markup=build_admin_users_global_bulk_actions_menu(
            current_filter=current_filter,
            current_page=current_page,
        ),
    )
    await callback.answer("Операция поставлена в очередь")


async def handle_admin_users_bulk_action(
    *,
    callback: CallbackQuery,
    settings: Settings,
    state: FSMContext,
    admin: AdminService,
    action_prefix: str,
    action_title: str,
    global_scope: bool,
    executor,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    callback_data = callback.data
    if callback_data is None:
        await callback.answer()
        return

    parsed = parse_admin_users_scope(callback_data, action_prefix)
    if parsed is None:
        await callback.answer("Не удалось определить область действия.", show_alert=True)
        return

    current_filter, current_page = parsed
    overview = await admin.get_users_overview(page=current_page, current_filter=current_filter)
    if global_scope:
        target_telegram_ids: list[int] = []
        total_pages = max((overview.total_filtered - 1) // BULK_USERS_PAGE_SIZE + 1, 1)
        for page in range(total_pages):
            batch = await admin.get_users_overview(
                page=page,
                page_size=BULK_USERS_PAGE_SIZE,
                current_filter=current_filter,
            )
            target_telegram_ids.extend(user.telegram_id for user in batch.recent_users)
        total_users = len(target_telegram_ids)
    else:
        target_telegram_ids = [user.telegram_id for user in overview.recent_users]
        total_users = len(target_telegram_ids)

    if total_users == 0:
        empty_message = (
            "В этом сегменте нет пользователей."
            if global_scope
            else "На этой странице нет пользователей."
        )
        await callback.answer(empty_message, show_alert=True)
        return

    await state.clear()
    await callback.answer("Операция запущена")

    processed_users = 0
    skipped_users = 0
    failed_users = 0
    affected_accesses = 0
    last_progress_update = 0.0

    async def update_progress(*, current_user_telegram_id: int | None, force: bool = False) -> None:
        nonlocal last_progress_update
        now = monotonic()
        should_update = force or processed_users == 0 or processed_users == total_users
        should_update = should_update or processed_users % BULK_PROGRESS_UPDATE_EVERY == 0
        should_update = should_update or (now - last_progress_update) >= BULK_PROGRESS_UPDATE_INTERVAL
        if not should_update:
            return

        await safe_edit_message(
            callback,
            text=build_admin_users_bulk_progress_text(
                action_title=action_title,
                current_filter=current_filter,
                global_scope=global_scope,
                total_users=total_users,
                processed_users=processed_users,
                affected_accesses=affected_accesses,
                skipped_users=skipped_users,
                failed_users=failed_users,
                current_user_telegram_id=current_user_telegram_id,
            ),
            reply_markup=build_admin_users_bulk_progress_menu(),
        )
        last_progress_update = now

    await update_progress(current_user_telegram_id=None, force=True)

    async def process_user(telegram_id: int) -> None:
        nonlocal processed_users
        nonlocal skipped_users
        nonlocal failed_users
        nonlocal affected_accesses

        try:
            affected_for_user, ok = await executor(telegram_id, telegram_user.id)
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
        await update_progress(current_user_telegram_id=telegram_id)

    for target_telegram_id in target_telegram_ids:
        await process_user(target_telegram_id)

    await update_progress(current_user_telegram_id=None, force=True)
    await safe_edit_message(
        callback,
        text=build_admin_users_bulk_result_text(
            action_title=action_title,
            current_filter=current_filter,
            global_scope=global_scope,
            total_users=total_users,
            affected_accesses=affected_accesses,
            skipped_users=skipped_users,
            failed_users=failed_users,
        ),
        reply_markup=build_admin_users_bulk_result_menu(
            current_filter=current_filter,
            current_page=current_page,
            global_scope=global_scope,
        ),
    )
