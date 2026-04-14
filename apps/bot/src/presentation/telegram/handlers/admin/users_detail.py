# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.admin import AdminService
from src.presentation.telegram.callbacks import ADMIN_USER_HISTORY_PREFIX, ADMIN_USER_VIEW_PREFIX
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import build_admin_user_detail_menu
from src.presentation.telegram.screens.admin import build_admin_user_history_text

from .common import answer_access_denied, is_admin_user, parse_telegram_id_from_callback
from .users_common import render_user_detail

router = Router(name="admin_users_detail")


@router.callback_query(F.data.startswith(ADMIN_USER_VIEW_PREFIX))
async def admin_user_view_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    callback_data = callback.data
    if callback_data is None:
        await callback.answer()
        return

    target_telegram_id = parse_telegram_id_from_callback(callback_data, ADMIN_USER_VIEW_PREFIX)
    if target_telegram_id is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    detail = await admin.get_user_detail(target_telegram_id)
    if detail is None:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return

    await state.clear()
    await render_user_detail(callback, detail)
    await callback.answer()


@router.callback_query(F.data.startswith(ADMIN_USER_HISTORY_PREFIX))
async def admin_user_history_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    callback_data = callback.data
    if callback_data is None:
        await callback.answer()
        return

    target_telegram_id = parse_telegram_id_from_callback(callback_data, ADMIN_USER_HISTORY_PREFIX)
    if target_telegram_id is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    detail = await admin.get_user_detail(target_telegram_id)
    if detail is None:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return

    await safe_edit_message(
        callback,
        text=build_admin_user_history_text(detail),
        reply_markup=build_admin_user_detail_menu(detail),
    )
    await callback.answer()
