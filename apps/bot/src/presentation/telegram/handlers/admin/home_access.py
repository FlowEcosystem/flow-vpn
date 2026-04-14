# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.runtime import AccessMode, RuntimeSettingsService
from src.presentation.telegram.callbacks import (
    ACTION_ADMIN_SET_FREE_ACCESS,
    ACTION_ADMIN_SET_MAX_VPN_ACCESSES,
    ADMIN_ACCESS_MODE_CALLBACKS,
    MENU_ADMIN_ACCESS,
)
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import build_access_mode_menu, build_admin_section_menu
from src.presentation.telegram.screens.admin import build_access_mode_text, build_max_vpn_accesses_prompt_text
from src.presentation.telegram.states import AdminMaxVpnAccessesState

from .common import answer_access_denied, is_admin_user

router = Router(name="admin_home_access")


@router.callback_query(F.data == MENU_ADMIN_ACCESS)
async def access_mode_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    runtime_settings: FromDishka[RuntimeSettingsService],
    state: FSMContext,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    access_mode = await runtime_settings.get_access_mode()
    max_vpn_accesses_per_user = await runtime_settings.get_max_vpn_accesses_per_user()
    await state.clear()
    await safe_edit_message(
        callback,
        text=build_access_mode_text(access_mode, max_vpn_accesses_per_user),
        reply_markup=build_access_mode_menu(current_mode=access_mode),
    )
    await callback.answer()


@router.callback_query(F.data.in_(ADMIN_ACCESS_MODE_CALLBACKS))
async def admin_access_mode_action_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    runtime_settings: FromDishka[RuntimeSettingsService],
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

    if callback_data == ACTION_ADMIN_SET_MAX_VPN_ACCESSES:
        current_limit = await runtime_settings.get_max_vpn_accesses_per_user()
        await state.set_state(AdminMaxVpnAccessesState.waiting_value)
        await safe_edit_message(
            callback,
            text=build_max_vpn_accesses_prompt_text(current_limit),
            reply_markup=build_admin_section_menu(
                action_text="🎛 Вернуться к настройкам",
                action_callback=MENU_ADMIN_ACCESS,
            ),
        )
        await callback.answer("Ожидаю число")
        return

    target_mode = (
        AccessMode.FREE_ACCESS
        if callback_data == ACTION_ADMIN_SET_FREE_ACCESS
        else AccessMode.BILLING_ENABLED
    )
    current_mode = await runtime_settings.get_access_mode()
    current_limit = await runtime_settings.get_max_vpn_accesses_per_user()
    if current_mode is not target_mode:
        current_mode = await runtime_settings.set_access_mode(target_mode)

    await state.clear()
    await safe_edit_message(
        callback,
        text=build_access_mode_text(current_mode, current_limit),
        reply_markup=build_access_mode_menu(current_mode=current_mode),
    )
    await callback.answer("Режим обновлён ✨")


@router.message(AdminMaxVpnAccessesState.waiting_value)
async def admin_max_vpn_accesses_message_handler(
    message: Message,
    settings: FromDishka[Settings],
    runtime_settings: FromDishka[RuntimeSettingsService],
    state: FSMContext,
) -> None:
    telegram_user = message.from_user
    if telegram_user is None or not is_admin_user(
        settings=settings,
        telegram_user_id=telegram_user.id,
    ):
        await state.clear()
        await answer_access_denied(message)
        return

    raw_value = (message.text or "").strip()
    if not raw_value.isdigit():
        await message.answer("Отправьте число от 0 до 99.")
        return

    limit = int(raw_value)
    if limit > 99:
        await message.answer("Слишком большое значение. Используйте число от 0 до 99.")
        return

    updated_limit = await runtime_settings.set_max_vpn_accesses_per_user(limit)
    current_mode = await runtime_settings.get_access_mode()
    await state.clear()
    await message.answer(
        build_access_mode_text(current_mode, updated_limit),
        reply_markup=build_access_mode_menu(current_mode=current_mode),
    )
