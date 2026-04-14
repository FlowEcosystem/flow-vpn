# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.promos import PromoService
from src.presentation.telegram.callbacks import ADMIN_PROMO_VIEW_PREFIX, MENU_ADMIN_PROMOS
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import (
    build_admin_promo_detail_menu,
    build_admin_promos_list_menu,
)
from src.presentation.telegram.screens.admin import (
    build_admin_promo_detail_text,
    build_admin_promos_list_text,
)

from .common import answer_access_denied, is_admin_user
from .promos_common import get_admin_promo_by_id, parse_promo_id

router = Router(name="admin_promos_list")


@router.callback_query(F.data == MENU_ADMIN_PROMOS)
async def admin_promos_list_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    promos: FromDishka[PromoService],
    state: FSMContext,
) -> None:
    if not is_admin_user(settings=settings, telegram_user_id=callback.from_user.id):
        await answer_access_denied(callback)
        return

    await state.clear()
    promo_list = await promos.list_admin_promos()
    await safe_edit_message(
        callback,
        text=build_admin_promos_list_text(promo_list),
        reply_markup=build_admin_promos_list_menu(promo_list),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(ADMIN_PROMO_VIEW_PREFIX))
async def admin_promo_view_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    promos: FromDishka[PromoService],
) -> None:
    if not is_admin_user(settings=settings, telegram_user_id=callback.from_user.id):
        await answer_access_denied(callback)
        return

    promo_id = parse_promo_id(callback.data or "", ADMIN_PROMO_VIEW_PREFIX)
    if promo_id is None:
        await callback.answer("Некорректный идентификатор.", show_alert=True)
        return

    promo = await get_admin_promo_by_id(promos, promo_id)
    if promo is None:
        await callback.answer("Промокод не найден.", show_alert=True)
        return

    await safe_edit_message(
        callback,
        text=build_admin_promo_detail_text(promo),
        reply_markup=build_admin_promo_detail_menu(promo),
    )
    await callback.answer()
