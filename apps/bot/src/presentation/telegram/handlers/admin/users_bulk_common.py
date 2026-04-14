# ruff: noqa: RUF001

from src.app.config import Settings
from src.application.admin import AdminBulkOperationsService, AdminService
from src.presentation.telegram.handlers.start import safe_edit_message

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from .bulk import enqueue_admin_users_bulk_operation as _enqueue_admin_users_bulk_operation
from .common import answer_access_denied, is_admin_user, parse_admin_users_scope


async def show_bulk_screen(
    *,
    callback: CallbackQuery,
    settings: Settings,
    admin: AdminService,
    state: FSMContext,
    action_prefix: str,
    parse_error_message: str,
    empty_message: str,
    is_empty,
    render_text,
    render_menu,
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
        await callback.answer(parse_error_message, show_alert=True)
        return

    current_filter, current_page = parsed
    overview = await admin.get_users_overview(
        page=current_page,
        current_filter=current_filter,
    )
    if is_empty(overview):
        await callback.answer(empty_message, show_alert=True)
        return

    await state.clear()
    await safe_edit_message(
        callback,
        text=render_text(overview),
        reply_markup=render_menu(
            current_filter=current_filter,
            current_page=current_page,
        ),
    )
    await callback.answer()


async def enqueue_global_bulk_operation(
    *,
    callback: CallbackQuery,
    settings: Settings,
    admin: AdminService,
    admin_bulk: AdminBulkOperationsService,
    state: FSMContext,
    action_prefix: str,
    action: str,
) -> None:
    await _enqueue_admin_users_bulk_operation(
        callback=callback,
        settings=settings,
        state=state,
        admin=admin,
        admin_bulk=admin_bulk,
        action_prefix=action_prefix,
        action=action,
    )


async def build_local_disable_executor(
    admin: AdminService,
    user_id: int,
    admin_id: int,
) -> tuple[int, bool]:
    detail = await admin.get_user_detail(user_id)
    if detail is None:
        return 0, False

    active_accesses = [access for access in detail.vpn_accesses if access.status == "active"]
    if not active_accesses:
        return 0, True

    affected = 0
    for access in active_accesses:
        result = await admin.disable_access(access.id, actor_telegram_id=admin_id)
        if result is None:
            return affected, False
        affected += 1
    return affected, True


async def build_local_delete_executor(
    admin: AdminService,
    user_id: int,
    admin_id: int,
) -> tuple[int, bool]:
    detail = await admin.get_user_detail(user_id)
    if detail is None:
        return 0, False

    if not detail.vpn_accesses:
        return 0, True

    affected = 0
    for access in detail.vpn_accesses:
        result = await admin.delete_access(access.id, actor_telegram_id=admin_id)
        if result is None:
            return affected, False
        affected += 1
    return affected, True
