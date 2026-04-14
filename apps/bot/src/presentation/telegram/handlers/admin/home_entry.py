# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.admin import AdminService
from src.presentation.telegram.callbacks import MENU_ADMIN_HOME
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import build_admin_menu
from src.presentation.telegram.screens.admin import build_admin_home_text

from .common import answer_access_denied, is_admin_user

router = Router(name="admin_home_entry")


@router.message(Command("admin"))
async def admin_entry_handler(
    message: Message,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    telegram_user = message.from_user
    if telegram_user is None or not is_admin_user(
        settings=settings,
        telegram_user_id=telegram_user.id,
    ):
        await answer_access_denied(message)
        return

    display_name = telegram_user.first_name or telegram_user.full_name or "admin"
    dashboard = await admin.get_dashboard()
    await state.clear()
    await message.answer(
        build_admin_home_text(display_name, dashboard),
        reply_markup=build_admin_menu(),
    )


@router.callback_query(F.data == MENU_ADMIN_HOME)
async def admin_home_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    display_name = telegram_user.first_name or telegram_user.full_name or "admin"
    dashboard = await admin.get_dashboard()
    await state.clear()
    await safe_edit_message(
        callback,
        text=build_admin_home_text(display_name, dashboard),
        reply_markup=build_admin_menu(),
    )
    await callback.answer()
