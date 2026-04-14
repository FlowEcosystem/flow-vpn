# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka

from src.application.promos import PromoService
from src.presentation.telegram.callbacks import ACTION_PROMO, MENU_PROMO
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.client import build_promo_menu, build_text_input_menu
from src.presentation.telegram.screens.client import build_promo_input_text, build_promo_text
from src.presentation.telegram.states import PromoCodeState

router = Router(name="client_promos_section")


@router.callback_query(F.data == MENU_PROMO)
async def promo_section_callback_handler(
    callback: CallbackQuery,
    promos: FromDishka[PromoService],
    state: FSMContext,
) -> None:
    overview = await promos.get_overview(callback.from_user.id)
    if overview is None:
        await callback.answer(
            "Профиль пока не найден. Отправьте /start ещё раз.",
            show_alert=True,
        )
        return

    await state.clear()
    await safe_edit_message(
        callback,
        text=build_promo_text(overview),
        reply_markup=build_promo_menu(overview),
    )
    await callback.answer()


@router.callback_query(F.data == ACTION_PROMO)
async def promo_action_callback_handler(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.set_state(PromoCodeState.waiting_code)
    await safe_edit_message(
        callback,
        text=build_promo_input_text(),
        reply_markup=build_text_input_menu(back_callback=MENU_PROMO),
    )
    await callback.answer()
