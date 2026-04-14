# ruff: noqa: RUF001

from src.application.admin.dto import AdminBulkOperationInfo

from .bulk_common import format_admin_bulk_operation_line


def build_admin_users_bulk_history_text(
    operations: tuple[AdminBulkOperationInfo, ...],
) -> str:
    if operations:
        history_block = "\n".join(format_admin_bulk_operation_line(op) for op in operations)
    else:
        history_block = "• История массовых операций пока пуста"

    return (
        "🗂 <b>История массовых операций</b>\n\n"
        "Здесь показаны последние глобальные задачи по пользователям.\n\n"
        f"{history_block}"
    )
