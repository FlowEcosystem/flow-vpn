"""Compatibility facade for admin bulk helpers."""

from .bulk_rendering import (
    build_admin_bulk_operation_menu,
    build_admin_bulk_operation_text,
    render_admin_bulk_operation_message,
)
from .bulk_ui import enqueue_admin_users_bulk_operation, handle_admin_users_bulk_action
from .bulk_worker import (
    execute_admin_bulk_operation_for_user,
    run_admin_bulk_operation,
    run_admin_bulk_operations_loop,
)
from src.application.admin import can_cancel_admin_bulk_operation, can_rollback_admin_bulk_operation

__all__ = [
    "build_admin_bulk_operation_menu",
    "build_admin_bulk_operation_text",
    "can_cancel_admin_bulk_operation",
    "can_rollback_admin_bulk_operation",
    "enqueue_admin_users_bulk_operation",
    "execute_admin_bulk_operation_for_user",
    "handle_admin_users_bulk_action",
    "render_admin_bulk_operation_message",
    "run_admin_bulk_operation",
    "run_admin_bulk_operations_loop",
]
