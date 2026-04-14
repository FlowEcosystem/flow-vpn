# ruff: noqa: RUF001

import uuid as uuid_module
from datetime import UTC, datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.admin import (
    ADMIN_BULK_ACTION_DISABLE,
    ADMIN_BULK_ACTION_ISSUE,
    ADMIN_BULK_ACTION_ROLLBACK_DISABLE,
    ADMIN_BULK_ACTION_ROLLBACK_ISSUE,
    AdminBulkOperationSnapshot,
    AdminBulkOperationsService,
)
from src.presentation.telegram.callbacks import (
    ADMIN_USERS_BULK_HISTORY_PREFIX,
    ADMIN_USERS_BULK_HISTORY_VIEW_PREFIX,
    ADMIN_USERS_BULK_OPERATION_CANCEL_PREFIX,
    ADMIN_USERS_BULK_OPERATION_REFRESH_PREFIX,
    ADMIN_USERS_BULK_OPERATION_ROLLBACK_PREFIX,
)
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import (
    build_admin_users_bulk_history_detail_menu,
    build_admin_users_bulk_history_menu,
)
from src.presentation.telegram.screens.admin import build_admin_users_bulk_history_text

from .bulk import (
    build_admin_bulk_operation_menu as _build_admin_bulk_operation_menu,
    build_admin_bulk_operation_text as _build_admin_bulk_operation_text,
    can_cancel_admin_bulk_operation as _can_cancel_admin_bulk_operation,
    can_rollback_admin_bulk_operation as _can_rollback_admin_bulk_operation,
    render_admin_bulk_operation_message as _render_admin_bulk_operation_message,
)
from .common import (
    answer_access_denied,
    is_admin_user,
    parse_admin_users_bulk_operation_scope,
    parse_admin_users_history_view,
    parse_admin_users_scope,
    parse_uuid_from_callback,
)

router = Router(name="admin_users_bulk_history")


@router.callback_query(F.data.startswith(ADMIN_USERS_BULK_HISTORY_PREFIX))
async def admin_users_bulk_history_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin_bulk: FromDishka[AdminBulkOperationsService],
    state,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    callback_data = callback.data
    if callback_data is None:
        await callback.answer()
        return

    parsed = parse_admin_users_scope(callback_data, ADMIN_USERS_BULK_HISTORY_PREFIX)
    if parsed is None:
        await callback.answer("Не удалось определить страницу.", show_alert=True)
        return

    current_filter, current_page = parsed
    operations = await admin_bulk.list_recent_operations()

    await state.clear()
    await safe_edit_message(
        callback,
        text=build_admin_users_bulk_history_text(operations),
        reply_markup=build_admin_users_bulk_history_menu(
            operations=operations,
            current_filter=current_filter,
            current_page=current_page,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(ADMIN_USERS_BULK_HISTORY_VIEW_PREFIX))
async def admin_users_bulk_history_view_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin_bulk: FromDishka[AdminBulkOperationsService],
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    parsed = parse_admin_users_history_view(callback.data or "")
    if parsed is None:
        await callback.answer("Не удалось определить операцию.", show_alert=True)
        return

    operation_id, current_filter, current_page = parsed
    operation = await admin_bulk.get_operation(operation_id)
    if operation is None:
        await callback.answer("Операция не найдена.", show_alert=True)
        return

    await safe_edit_message(
        callback,
        text=_build_admin_bulk_operation_text(operation),
        reply_markup=build_admin_users_bulk_history_detail_menu(
            operation_id=operation.id,
            current_filter=current_filter,
            current_page=current_page,
            can_cancel=_can_cancel_admin_bulk_operation(operation),
            can_rollback=_can_rollback_admin_bulk_operation(operation),
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(ADMIN_USERS_BULK_OPERATION_REFRESH_PREFIX))
async def admin_users_bulk_operation_refresh_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin_bulk: FromDishka[AdminBulkOperationsService],
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    operation_id = parse_uuid_from_callback(
        callback.data or "",
        ADMIN_USERS_BULK_OPERATION_REFRESH_PREFIX,
    )
    if operation_id is None:
        await callback.answer("Не удалось определить операцию.", show_alert=True)
        return

    operation = await admin_bulk.get_operation(operation_id)
    if operation is None:
        await callback.answer("Операция не найдена.", show_alert=True)
        return

    await safe_edit_message(
        callback,
        text=_build_admin_bulk_operation_text(operation),
        reply_markup=_build_admin_bulk_operation_menu(operation),
    )
    await callback.answer("Статус обновлён")


@router.callback_query(F.data.startswith(ADMIN_USERS_BULK_OPERATION_CANCEL_PREFIX))
async def admin_users_bulk_operation_cancel_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin_bulk: FromDishka[AdminBulkOperationsService],
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    operation_id = parse_uuid_from_callback(
        callback.data or "",
        ADMIN_USERS_BULK_OPERATION_CANCEL_PREFIX,
    )
    if operation_id is None:
        await callback.answer("Не удалось определить операцию.", show_alert=True)
        return

    operation = await admin_bulk.get_operation(operation_id)
    if operation is None:
        await callback.answer("Операция не найдена.", show_alert=True)
        return
    if not _can_cancel_admin_bulk_operation(operation):
        await callback.answer("Эту операцию уже нельзя отменить.", show_alert=True)
        return

    await admin_bulk.cancel_operation(operation.id)
    updated = await admin_bulk.get_operation(operation.id)
    if updated is None:
        await callback.answer("Операция не найдена.", show_alert=True)
        return

    await _render_admin_bulk_operation_message(callback.bot, updated)
    await safe_edit_message(
        callback,
        text=_build_admin_bulk_operation_text(updated),
        reply_markup=_build_admin_bulk_operation_menu(updated),
    )
    await callback.answer("Операция отменена")


@router.callback_query(F.data.startswith(ADMIN_USERS_BULK_OPERATION_ROLLBACK_PREFIX))
async def admin_users_bulk_operation_rollback_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin_bulk: FromDishka[AdminBulkOperationsService],
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    parsed = parse_admin_users_bulk_operation_scope(
        callback.data or "",
        ADMIN_USERS_BULK_OPERATION_ROLLBACK_PREFIX,
    )
    if parsed is None:
        await callback.answer("Не удалось определить операцию.", show_alert=True)
        return

    source_operation_id, current_filter, current_page = parsed
    source_operation = await admin_bulk.get_operation(source_operation_id)
    if source_operation is None:
        await callback.answer("Исходная операция не найдена.", show_alert=True)
        return
    if not _can_rollback_admin_bulk_operation(source_operation):
        await callback.answer("Для этой операции откат недоступен.", show_alert=True)
        return

    rollback_action = {
        ADMIN_BULK_ACTION_ISSUE: ADMIN_BULK_ACTION_ROLLBACK_ISSUE,
        ADMIN_BULK_ACTION_DISABLE: ADMIN_BULK_ACTION_ROLLBACK_DISABLE,
    }.get(source_operation.action)
    if rollback_action is None:
        await callback.answer("Для этой операции откат недоступен.", show_alert=True)
        return

    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    rollback_id = uuid_module.uuid4()
    queued_operation = AdminBulkOperationSnapshot(
        id=rollback_id,
        admin_telegram_id=telegram_user.id,
        action=rollback_action,
        source_operation_id=source_operation.id,
        target_segment=source_operation.target_segment,
        source_page=current_page,
        is_global=True,
        status="pending",
        total_users=len(source_operation.target_telegram_ids),
        processed_users=0,
        affected_accesses=0,
        skipped_users=0,
        failed_users=0,
        target_telegram_ids=source_operation.target_telegram_ids,
        message_chat_id=0,
        message_id=0,
        last_error=None,
        created_at=datetime.now(UTC),
        started_at=None,
        completed_at=None,
    )
    status_message = await message.answer(
        _build_admin_bulk_operation_text(queued_operation),
        reply_markup=_build_admin_bulk_operation_menu(queued_operation),
    )

    await admin_bulk.enqueue_operation(
        operation_id=rollback_id,
        admin_telegram_id=telegram_user.id,
        action=rollback_action,
        source_operation_id=source_operation.id,
        target_segment=source_operation.target_segment,
        source_page=current_page,
        is_global=True,
        target_telegram_ids=source_operation.target_telegram_ids,
        message_chat_id=status_message.chat.id,
        message_id=status_message.message_id,
    )

    await callback.answer("Откат поставлен в очередь")
