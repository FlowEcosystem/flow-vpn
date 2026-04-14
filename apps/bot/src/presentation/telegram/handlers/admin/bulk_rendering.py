# ruff: noqa: RUF001

import structlog
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from src.application.admin import (
    AdminBulkOperationSnapshot,
    AdminUsersFilter,
    can_cancel_admin_bulk_operation,
    can_rollback_admin_bulk_operation,
    get_admin_bulk_action_title,
)
from src.presentation.telegram.keyboards.admin import (
    build_admin_users_bulk_operation_status_menu,
    build_admin_users_bulk_result_menu,
)
from src.presentation.telegram.screens.admin import (
    build_admin_users_bulk_cancelled_text,
    build_admin_users_bulk_failed_text,
    build_admin_users_bulk_progress_text,
    build_admin_users_bulk_queued_text,
    build_admin_users_bulk_result_text,
)

logger = structlog.get_logger(__name__)


def build_admin_bulk_operation_text(operation: AdminBulkOperationSnapshot) -> str:
    current_filter = AdminUsersFilter(operation.target_segment)
    action_title = get_admin_bulk_action_title(operation.action)
    if operation.status == "pending":
        return build_admin_users_bulk_queued_text(
            action_title=action_title,
            current_filter=current_filter,
            global_scope=operation.is_global,
            total_users=operation.total_users,
        )
    if operation.status == "running":
        return build_admin_users_bulk_progress_text(
            action_title=action_title,
            current_filter=current_filter,
            global_scope=operation.is_global,
            total_users=operation.total_users,
            processed_users=operation.processed_users,
            affected_accesses=operation.affected_accesses,
            skipped_users=operation.skipped_users,
            failed_users=operation.failed_users,
        )
    if operation.status == "failed":
        return build_admin_users_bulk_failed_text(
            action_title=action_title,
            current_filter=current_filter,
            global_scope=operation.is_global,
            total_users=operation.total_users,
            processed_users=operation.processed_users,
            affected_accesses=operation.affected_accesses,
            skipped_users=operation.skipped_users,
            failed_users=operation.failed_users,
            error_message=operation.last_error,
        )
    if operation.status == "cancelled":
        return build_admin_users_bulk_cancelled_text(
            action_title=action_title,
            current_filter=current_filter,
            global_scope=operation.is_global,
            total_users=operation.total_users,
            processed_users=operation.processed_users,
            affected_accesses=operation.affected_accesses,
            skipped_users=operation.skipped_users,
            failed_users=operation.failed_users,
        )
    return build_admin_users_bulk_result_text(
        action_title=action_title,
        current_filter=current_filter,
        global_scope=operation.is_global,
        total_users=operation.total_users,
        affected_accesses=operation.affected_accesses,
        skipped_users=operation.skipped_users,
        failed_users=operation.failed_users,
    )


def build_admin_bulk_operation_menu(operation: AdminBulkOperationSnapshot):
    current_filter = AdminUsersFilter(operation.target_segment)
    if can_cancel_admin_bulk_operation(operation) or can_rollback_admin_bulk_operation(operation):
        return build_admin_users_bulk_operation_status_menu(
            operation_id=operation.id,
            current_filter=current_filter,
            current_page=operation.source_page,
            global_scope=operation.is_global,
            can_cancel=can_cancel_admin_bulk_operation(operation),
            can_rollback=can_rollback_admin_bulk_operation(operation),
        )
    return build_admin_users_bulk_result_menu(
        current_filter=current_filter,
        current_page=operation.source_page,
        global_scope=operation.is_global,
    )


async def render_admin_bulk_operation_message(
    bot: Bot,
    operation: AdminBulkOperationSnapshot,
) -> None:
    try:
        await bot.edit_message_text(
            text=build_admin_bulk_operation_text(operation),
            chat_id=operation.message_chat_id,
            message_id=operation.message_id,
            reply_markup=build_admin_bulk_operation_menu(operation),
        )
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc):
            logger.warning(
                "admin_bulk_operation_message_update_failed",
                operation_id=str(operation.id),
                error=str(exc),
            )
