# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.presentation.telegram.callbacks import (
    ADMIN_ACTION_CALLBACKS,
    ADMIN_SECTION_CALLBACKS,
    MENU_ADMIN_ACCESS,
    MENU_ADMIN_BROADCASTS,
    MENU_ADMIN_HOME,
    MENU_ADMIN_PROMOS,
    MENU_ADMIN_SUPPORT,
    MENU_ADMIN_USERS,
)
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import build_admin_section_menu
from src.presentation.telegram.screens.admin import ADMIN_ACTION_FEEDBACK, ADMIN_SECTION_SCREENS

from .common import answer_access_denied, is_admin_user

router = Router(name="admin_home_sections")


@router.callback_query(
    F.data.in_(
        ADMIN_SECTION_CALLBACKS
        - {
            MENU_ADMIN_HOME,
            MENU_ADMIN_ACCESS,
            MENU_ADMIN_USERS,
            MENU_ADMIN_PROMOS,
            MENU_ADMIN_SUPPORT,
            MENU_ADMIN_BROADCASTS,
        }
    )
)
async def admin_section_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
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

    screen = ADMIN_SECTION_SCREENS[callback_data]
    await state.clear()
    await safe_edit_message(
        callback,
        text=screen.text,
        reply_markup=build_admin_section_menu(
            action_text=screen.action_text,
            action_callback=screen.action_callback,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.in_(ADMIN_ACTION_CALLBACKS))
async def admin_action_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
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

    await state.clear()
    await callback.answer(ADMIN_ACTION_FEEDBACK[callback_data], show_alert=True)
