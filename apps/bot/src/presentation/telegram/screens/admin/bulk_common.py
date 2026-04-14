# ruff: noqa: RUF001

from src.application.admin.dto import AdminBulkOperationInfo, AdminUsersFilter
from src.presentation.telegram.datetime import format_datetime_msk


def format_users_filter(value: AdminUsersFilter) -> str:
    return {
        AdminUsersFilter.ALL: "все",
        AdminUsersFilter.WITH_ACCESS: "с доступом",
        AdminUsersFilter.WITHOUT_ACCESS: "без доступа",
    }[value]


def format_admin_bulk_operation_line(operation: AdminBulkOperationInfo) -> str:
    filter_label = format_users_filter(AdminUsersFilter(operation.target_segment))
    scope_label = "все" if operation.is_global else "страница"
    created_at = format_datetime_msk(operation.created_at)
    return (
        f"{format_admin_bulk_operation_status(operation.status)} "
        f"<b>{format_admin_bulk_operation_action(operation.action)}</b> "
        f"· {scope_label} · {filter_label}\n"
        f"• {operation.processed_users:,}/{operation.total_users:,} "
        f"· подписок {operation.affected_accesses:,} "
        f"· {created_at}"
    )


def format_admin_bulk_operation_action(action: str) -> str:
    return {
        "issue": "выдача",
        "disable": "отключение",
        "delete": "удаление",
        "rollback_issue": "откат выдачи",
        "rollback_disable": "откат отключения",
    }.get(action, action)


def format_admin_bulk_operation_status(status: str) -> str:
    return {
        "pending": "🕒",
        "running": "⏳",
        "done": "✅",
        "failed": "❌",
        "cancelled": "⛔",
    }.get(status, "•")


def build_progress_bar(percent: int) -> str:
    total_slots = 10
    filled = round(percent / 100 * total_slots)
    return "█" * filled + "░" * (total_slots - filled)
