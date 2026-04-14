# ruff: noqa: RUF001

from uuid import UUID

import structlog
from aiogram.types import CallbackQuery, Message

from src.app.config import Settings
from src.application.admin import AdminUsersFilter
from src.presentation.telegram.callbacks import (
    ADMIN_USERS_BULK_HISTORY_VIEW_PREFIX,
    ADMIN_USERS_FILTER_PREFIX,
    ADMIN_USERS_PAGE_PREFIX,
)

logger = structlog.get_logger(__name__)


def is_admin_user(*, settings: Settings, telegram_user_id: int) -> bool:
    return settings.is_admin(telegram_user_id)


def parse_telegram_id_from_callback(data: str, prefix: str) -> int | None:
    if not data.startswith(prefix):
        return None

    raw_value = data.removeprefix(prefix)
    if not raw_value.isdigit():
        return None

    return int(raw_value)


def parse_admin_users_page(data: str) -> tuple[AdminUsersFilter, int] | None:
    if not data.startswith(ADMIN_USERS_PAGE_PREFIX):
        return None

    raw_value = data.removeprefix(ADMIN_USERS_PAGE_PREFIX)
    filter_value, separator, page_value = raw_value.partition(":")
    if not separator or not page_value.isdigit():
        return None

    try:
        current_filter = AdminUsersFilter(filter_value)
    except ValueError:
        return None

    return current_filter, int(page_value)


def parse_admin_users_filter(data: str) -> AdminUsersFilter | None:
    if not data.startswith(ADMIN_USERS_FILTER_PREFIX):
        return None

    raw_value = data.removeprefix(ADMIN_USERS_FILTER_PREFIX)
    try:
        return AdminUsersFilter(raw_value)
    except ValueError:
        return None


def parse_uuid_from_callback(data: str, prefix: str) -> UUID | None:
    if not data.startswith(prefix):
        return None

    raw_value = data.removeprefix(prefix)
    try:
        return UUID(raw_value)
    except ValueError:
        return None


def parse_admin_users_scope(data: str, prefix: str) -> tuple[AdminUsersFilter, int] | None:
    if not data.startswith(prefix):
        return None

    raw_value = data.removeprefix(prefix)
    filter_value, separator, page_value = raw_value.partition(":")
    if not separator or not page_value.isdigit():
        return None

    try:
        current_filter = AdminUsersFilter(filter_value)
    except ValueError:
        return None

    return current_filter, int(page_value)


def parse_admin_users_history_view(data: str) -> tuple[UUID, AdminUsersFilter, int] | None:
    if not data.startswith(ADMIN_USERS_BULK_HISTORY_VIEW_PREFIX):
        return None

    raw_value = data.removeprefix(ADMIN_USERS_BULK_HISTORY_VIEW_PREFIX)
    operation_id_value, separator, scope_value = raw_value.partition(":")
    if not separator:
        return None

    try:
        operation_id = UUID(operation_id_value)
    except ValueError:
        return None

    filter_value, separator, page_value = scope_value.partition(":")
    if not separator or not page_value.isdigit():
        return None

    try:
        current_filter = AdminUsersFilter(filter_value)
    except ValueError:
        return None

    return operation_id, current_filter, int(page_value)


def parse_admin_users_bulk_operation_scope(
    data: str,
    prefix: str,
) -> tuple[UUID, AdminUsersFilter, int] | None:
    if not data.startswith(prefix):
        return None

    raw_value = data.removeprefix(prefix)
    operation_id_value, separator, scope_value = raw_value.partition(":")
    if not separator:
        return None

    try:
        operation_id = UUID(operation_id_value)
    except ValueError:
        return None

    filter_value, separator, page_value = scope_value.partition(":")
    if not separator or not page_value.isdigit():
        return None

    try:
        current_filter = AdminUsersFilter(filter_value)
    except ValueError:
        return None

    return operation_id, current_filter, int(page_value)


async def answer_access_denied(target: Message | CallbackQuery) -> None:
    user = target.from_user
    logger.warning(
        "admin_access_denied",
        user_id=user.id if user else None,
        username=user.username if user else None,
    )
    if isinstance(target, Message):
        await target.answer("⛔ Доступ к этой панели ограничен.")
        return

    await target.answer("⛔ У вас нет доступа к этой панели.", show_alert=True)
