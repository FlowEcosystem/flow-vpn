# ruff: noqa: RUF001

from uuid import UUID

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.application.promos import PromoService
from src.presentation.telegram.callbacks import (
    PROMO_APPLY_PREFIX,
    PROMO_SELECT_ACCESS_PREFIX,
)
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.client import build_promo_menu
from src.presentation.telegram.screens.client import build_promo_result_text
from src.presentation.telegram.states import PromoCodeState

from .promos_common import handle_promo_apply_by_code, handle_promo_apply_by_code_message

router = Router(name="client_promos_apply")


@router.callback_query(F.data.startswith(PROMO_APPLY_PREFIX))
async def promo_apply_callback_handler(
    callback: CallbackQuery,
    promos: FromDishka[PromoService],
    state: FSMContext,
) -> None:
    code = (callback.data or "").removeprefix(PROMO_APPLY_PREFIX)
    if not code:
        await callback.answer("Неверный промокод.", show_alert=True)
        return

    await state.clear()
    await handle_promo_apply_by_code(callback=callback, code=code, promos=promos)


@router.callback_query(F.data.startswith(PROMO_SELECT_ACCESS_PREFIX))
async def promo_select_access_callback_handler(
    callback: CallbackQuery,
    promos: FromDishka[PromoService],
) -> None:
    raw = (callback.data or "").removeprefix(PROMO_SELECT_ACCESS_PREFIX)
    parts = raw.split(":", 1)
    if len(parts) != 2:
        await callback.answer("Неверные данные.", show_alert=True)
        return

    code, access_id_str = parts
    try:
        access_id = UUID(access_id_str)
    except ValueError:
        await callback.answer("Неверный идентификатор подписки.", show_alert=True)
        return

    result = await promos.apply(
        callback.from_user.id,
        code=code,
        target_access_id=access_id,
    )
    overview = await promos.get_overview(callback.from_user.id)
    await safe_edit_message(
        callback,
        text=build_promo_result_text(result),
        reply_markup=build_promo_menu(overview),
    )
    await callback.answer()


@router.message(PromoCodeState.waiting_code)
async def promo_message_handler(
    message: Message,
    promos: FromDishka[PromoService],
    state: FSMContext,
) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        await state.clear()
        await message.answer("Не удалось определить профиль. Отправьте /start ещё раз.")
        return

    code = (message.text or "").strip()
    await state.clear()
    await handle_promo_apply_by_code_message(message=message, code=code, promos=promos)
