# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.admin import (
    ADMIN_BULK_ACTION_DELETE,
    ADMIN_BULK_ACTION_DISABLE,
    ADMIN_BULK_ACTION_ISSUE,
    AdminBulkOperationsService,
    AdminService,
)
from src.presentation.telegram.callbacks import (
    ADMIN_USERS_BULK_DELETE_CONFIRM_PREFIX,
    ADMIN_USERS_BULK_DISABLE_CONFIRM_PREFIX,
    ADMIN_USERS_BULK_ISSUE_CONFIRM_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_DELETE_CONFIRM_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_DISABLE_CONFIRM_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_ISSUE_CONFIRM_PREFIX,
)

from .bulk import handle_admin_users_bulk_action as _handle_admin_users_bulk_action
from .users_bulk_common import (
    build_local_delete_executor,
    build_local_disable_executor,
    enqueue_global_bulk_operation,
)

router = Router(name="admin_users_bulk_actions")


@router.callback_query(F.data.startswith(ADMIN_USERS_BULK_ISSUE_CONFIRM_PREFIX))
async def admin_users_bulk_issue_confirm_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    async def executor(user_id: int, admin_id: int) -> tuple[int, bool]:
        detail = await admin.issue_access(
            user_id,
            actor_telegram_id=admin_id,
        )
        return (1, detail is not None)

    await _handle_admin_users_bulk_action(
        callback=callback,
        settings=settings,
        state=state,
        admin=admin,
        action_prefix=ADMIN_USERS_BULK_ISSUE_CONFIRM_PREFIX,
        action_title="Массовая выдача подписок",
        global_scope=False,
        executor=executor,
    )


@router.callback_query(F.data.startswith(ADMIN_USERS_GLOBAL_BULK_ISSUE_CONFIRM_PREFIX))
async def admin_users_global_bulk_issue_confirm_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    admin_bulk: FromDishka[AdminBulkOperationsService],
    state: FSMContext,
) -> None:
    await enqueue_global_bulk_operation(
        callback=callback,
        settings=settings,
        admin=admin,
        admin_bulk=admin_bulk,
        state=state,
        action_prefix=ADMIN_USERS_GLOBAL_BULK_ISSUE_CONFIRM_PREFIX,
        action=ADMIN_BULK_ACTION_ISSUE,
    )


@router.callback_query(F.data.startswith(ADMIN_USERS_BULK_DISABLE_CONFIRM_PREFIX))
async def admin_users_bulk_disable_confirm_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    async def executor(user_id: int, admin_id: int) -> tuple[int, bool]:
        return await build_local_disable_executor(admin, user_id, admin_id)

    await _handle_admin_users_bulk_action(
        callback=callback,
        settings=settings,
        state=state,
        admin=admin,
        action_prefix=ADMIN_USERS_BULK_DISABLE_CONFIRM_PREFIX,
        action_title="Массовое отключение подписок",
        global_scope=False,
        executor=executor,
    )


@router.callback_query(F.data.startswith(ADMIN_USERS_GLOBAL_BULK_DISABLE_CONFIRM_PREFIX))
async def admin_users_global_bulk_disable_confirm_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    admin_bulk: FromDishka[AdminBulkOperationsService],
    state: FSMContext,
) -> None:
    await enqueue_global_bulk_operation(
        callback=callback,
        settings=settings,
        admin=admin,
        admin_bulk=admin_bulk,
        state=state,
        action_prefix=ADMIN_USERS_GLOBAL_BULK_DISABLE_CONFIRM_PREFIX,
        action=ADMIN_BULK_ACTION_DISABLE,
    )


@router.callback_query(F.data.startswith(ADMIN_USERS_BULK_DELETE_CONFIRM_PREFIX))
async def admin_users_bulk_delete_confirm_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    async def executor(user_id: int, admin_id: int) -> tuple[int, bool]:
        return await build_local_delete_executor(admin, user_id, admin_id)

    await _handle_admin_users_bulk_action(
        callback=callback,
        settings=settings,
        state=state,
        admin=admin,
        action_prefix=ADMIN_USERS_BULK_DELETE_CONFIRM_PREFIX,
        action_title="Массовое удаление подписок",
        global_scope=False,
        executor=executor,
    )


@router.callback_query(F.data.startswith(ADMIN_USERS_GLOBAL_BULK_DELETE_CONFIRM_PREFIX))
async def admin_users_global_bulk_delete_confirm_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    admin_bulk: FromDishka[AdminBulkOperationsService],
    state: FSMContext,
) -> None:
    await enqueue_global_bulk_operation(
        callback=callback,
        settings=settings,
        admin=admin,
        admin_bulk=admin_bulk,
        state=state,
        action_prefix=ADMIN_USERS_GLOBAL_BULK_DELETE_CONFIRM_PREFIX,
        action=ADMIN_BULK_ACTION_DELETE,
    )
