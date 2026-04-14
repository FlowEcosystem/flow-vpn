# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.broadcasts import BroadcastsService
from src.presentation.telegram.callbacks import MENU_ADMIN_BROADCASTS
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import build_admin_broadcasts_menu
from src.presentation.telegram.screens.admin import build_admin_broadcasts_text

from .common import answer_access_denied, is_admin_user

router = Router(name="admin_broadcasts_list")


@router.callback_query(F.data == MENU_ADMIN_BROADCASTS)
async def admin_broadcasts_list_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    broadcasts_service: FromDishka[BroadcastsService],
    state: FSMContext,
) -> None:
    if not is_admin_user(settings=settings, telegram_user_id=callback.from_user.id):
        await answer_access_denied(callback)
        return

    await state.clear()
    broadcasts = await broadcasts_service.list_recent()
    await safe_edit_message(
        callback,
        text=build_admin_broadcasts_text(broadcasts),
        reply_markup=build_admin_broadcasts_menu(broadcasts),
    )
    await callback.answer()
