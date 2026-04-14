# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.promos import PromoService
from src.presentation.telegram.callbacks import (
    ACTION_ADMIN_PROMOS,
    ADMIN_PROMO_DELETE_PREFIX,
    ADMIN_PROMO_TOGGLE_PREFIX,
)
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import (
    build_admin_promo_create_cancel_menu,
    build_admin_promo_detail_menu,
    build_admin_promos_list_menu,
)
from src.presentation.telegram.screens.admin import (
    build_admin_promo_create_code_text,
    build_admin_promo_detail_text,
    build_admin_promos_list_text,
)
from src.presentation.telegram.states import AdminPromoCreationState

from .common import answer_access_denied, is_admin_user
from .promos_common import get_admin_promo_by_id, parse_promo_id

router = Router(name="admin_promos_actions")


@router.callback_query(F.data == ACTION_ADMIN_PROMOS)
async def admin_promo_create_start_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    state: FSMContext,
) -> None:
    if not is_admin_user(settings=settings, telegram_user_id=callback.from_user.id):
        await answer_access_denied(callback)
        return

    await state.set_state(AdminPromoCreationState.waiting_code)
    await safe_edit_message(
        callback,
        text=build_admin_promo_create_code_text(),
        reply_markup=build_admin_promo_create_cancel_menu(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(ADMIN_PROMO_TOGGLE_PREFIX))
async def admin_promo_toggle_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    promos: FromDishka[PromoService],
) -> None:
    if not is_admin_user(settings=settings, telegram_user_id=callback.from_user.id):
        await answer_access_denied(callback)
        return

    promo_id = parse_promo_id(callback.data or "", ADMIN_PROMO_TOGGLE_PREFIX)
    if promo_id is None:
        await callback.answer("Некорректный идентификатор.", show_alert=True)
        return

    current = await get_admin_promo_by_id(promos, promo_id)
    if current is None:
        await callback.answer("Промокод не найден.", show_alert=True)
        return

    promo = await promos.toggle_promo(promo_id, is_active=not current.is_active)
    if promo is None:
        await callback.answer("Не удалось обновить статус.", show_alert=True)
        return

    await safe_edit_message(
        callback,
        text=build_admin_promo_detail_text(promo),
        reply_markup=build_admin_promo_detail_menu(promo),
    )
    status_label = "активирован ✅" if promo.is_active else "деактивирован ⛔"
    await callback.answer(f"Промокод {status_label}")


@router.callback_query(F.data.startswith(ADMIN_PROMO_DELETE_PREFIX))
async def admin_promo_delete_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    promos: FromDishka[PromoService],
) -> None:
    if not is_admin_user(settings=settings, telegram_user_id=callback.from_user.id):
        await answer_access_denied(callback)
        return

    promo_id = parse_promo_id(callback.data or "", ADMIN_PROMO_DELETE_PREFIX)
    if promo_id is None:
        await callback.answer("Некорректный идентификатор.", show_alert=True)
        return

    deleted = await promos.delete_promo(promo_id)
    if not deleted:
        await callback.answer("Промокод не найден.", show_alert=True)
        return

    promo_list = await promos.list_admin_promos()
    await safe_edit_message(
        callback,
        text=build_admin_promos_list_text(promo_list),
        reply_markup=build_admin_promos_list_menu(promo_list),
    )
    await callback.answer("Промокод удалён 🗑")
