# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.promos import NewPromoCodeData, PromoService
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import (
    build_admin_promo_create_cancel_menu,
    build_admin_promo_detail_menu,
    build_admin_promo_scope_menu,
    build_admin_promo_type_menu,
)
from src.presentation.telegram.screens.admin import (
    build_admin_promo_create_bonus_text,
    build_admin_promo_create_code_text,
    build_admin_promo_create_limit_text,
    build_admin_promo_create_scope_text,
    build_admin_promo_create_title_text,
    build_admin_promo_create_type_text,
    build_admin_promo_detail_text,
)
from src.presentation.telegram.states import AdminPromoCreationState
from src.presentation.telegram.callbacks import ADMIN_PROMO_SCOPE_PREFIX, ADMIN_PROMO_TYPE_PREFIX

from .common import answer_access_denied, is_admin_user

router = Router(name="admin_promos_create")


@router.message(AdminPromoCreationState.waiting_code)
async def admin_promo_create_code_message_handler(
    message: Message,
    settings: FromDishka[Settings],
    state: FSMContext,
) -> None:
    telegram_user = message.from_user
    if telegram_user is None or not is_admin_user(
        settings=settings, telegram_user_id=telegram_user.id
    ):
        await state.clear()
        await answer_access_denied(message)
        return

    code = (message.text or "").strip().upper()
    if not code or not all(c.isalnum() or c in "-_" for c in code):
        await message.answer(
            "Код может содержать только латинские буквы, цифры, дефис и подчёркивание.\n"
            "Попробуйте ещё раз.",
            reply_markup=build_admin_promo_create_cancel_menu(),
        )
        return

    await state.update_data(promo_code=code)
    await state.set_state(AdminPromoCreationState.waiting_title)
    await message.answer(
        build_admin_promo_create_title_text(code),
        reply_markup=build_admin_promo_create_cancel_menu(),
    )


@router.message(AdminPromoCreationState.waiting_title)
async def admin_promo_create_title_message_handler(
    message: Message,
    settings: FromDishka[Settings],
    state: FSMContext,
) -> None:
    telegram_user = message.from_user
    if telegram_user is None or not is_admin_user(
        settings=settings, telegram_user_id=telegram_user.id
    ):
        await state.clear()
        await answer_access_denied(message)
        return

    title = (message.text or "").strip()
    if not title:
        await message.answer(
            "Название не может быть пустым. Попробуйте ещё раз.",
            reply_markup=build_admin_promo_create_cancel_menu(),
        )
        return

    state_data = await state.get_data()
    code = state_data["promo_code"]
    await state.update_data(promo_title=title)
    await state.set_state(AdminPromoCreationState.waiting_type)
    await message.answer(
        build_admin_promo_create_type_text(code, title),
        reply_markup=build_admin_promo_type_menu(),
    )


@router.callback_query(
    AdminPromoCreationState.waiting_type,
    F.data.startswith(ADMIN_PROMO_TYPE_PREFIX),
)
async def admin_promo_create_type_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    state: FSMContext,
) -> None:
    if not is_admin_user(settings=settings, telegram_user_id=callback.from_user.id):
        await answer_access_denied(callback)
        return

    promo_type = (callback.data or "").removeprefix(ADMIN_PROMO_TYPE_PREFIX)
    state_data = await state.get_data()
    code = state_data["promo_code"]
    title = state_data["promo_title"]

    if promo_type == "infinite":
        await state.update_data(promo_is_infinite=True, promo_bonus_days=0)
        await state.set_state(AdminPromoCreationState.waiting_scope)
        await safe_edit_message(
            callback,
            text=build_admin_promo_create_scope_text(code, title, "♾️ бессрочная"),
            reply_markup=build_admin_promo_scope_menu(),
        )
    else:
        await state.update_data(promo_is_infinite=False)
        await state.set_state(AdminPromoCreationState.waiting_bonus_days)
        await safe_edit_message(
            callback,
            text=build_admin_promo_create_bonus_text(code, title),
            reply_markup=build_admin_promo_create_cancel_menu(),
        )
    await callback.answer()


@router.message(AdminPromoCreationState.waiting_bonus_days)
async def admin_promo_create_bonus_message_handler(
    message: Message,
    settings: FromDishka[Settings],
    state: FSMContext,
) -> None:
    telegram_user = message.from_user
    if telegram_user is None or not is_admin_user(
        settings=settings, telegram_user_id=telegram_user.id
    ):
        await state.clear()
        await answer_access_denied(message)
        return

    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) < 1:
        await message.answer(
            "Введите число дней больше нуля (например, <b>30</b>).",
            reply_markup=build_admin_promo_create_cancel_menu(),
        )
        return

    state_data = await state.get_data()
    code = state_data["promo_code"]
    title = state_data["promo_title"]
    bonus_days = int(raw)
    await state.update_data(promo_bonus_days=bonus_days)
    await state.set_state(AdminPromoCreationState.waiting_scope)
    await message.answer(
        build_admin_promo_create_scope_text(code, title, f"+{bonus_days} дн."),
        reply_markup=build_admin_promo_scope_menu(),
    )


@router.callback_query(
    AdminPromoCreationState.waiting_scope,
    F.data.startswith(ADMIN_PROMO_SCOPE_PREFIX),
)
async def admin_promo_create_scope_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    state: FSMContext,
) -> None:
    if not is_admin_user(settings=settings, telegram_user_id=callback.from_user.id):
        await answer_access_denied(callback)
        return

    scope = (callback.data or "").removeprefix(ADMIN_PROMO_SCOPE_PREFIX)
    apply_to_all = scope == "all"
    await state.update_data(promo_apply_to_all=apply_to_all)

    state_data = await state.get_data()
    code = state_data["promo_code"]
    title = state_data["promo_title"]
    is_infinite = state_data.get("promo_is_infinite", False)
    bonus_days = state_data.get("promo_bonus_days", 0)
    bonus_label = "♾️ бессрочная" if is_infinite else f"+{bonus_days} дн."
    scope_label = "все активные" if apply_to_all else "первая активная"

    await state.set_state(AdminPromoCreationState.waiting_max_redemptions)
    await safe_edit_message(
        callback,
        text=build_admin_promo_create_limit_text(code, title, bonus_label, scope_label),
        reply_markup=build_admin_promo_create_cancel_menu(),
    )
    await callback.answer()


@router.message(AdminPromoCreationState.waiting_max_redemptions)
async def admin_promo_create_limit_message_handler(
    message: Message,
    settings: FromDishka[Settings],
    promos: FromDishka[PromoService],
    state: FSMContext,
) -> None:
    telegram_user = message.from_user
    if telegram_user is None or not is_admin_user(
        settings=settings, telegram_user_id=telegram_user.id
    ):
        await state.clear()
        await answer_access_denied(message)
        return

    raw = (message.text or "").strip()
    if not raw.isdigit():
        await message.answer(
            "Введите число (например, <b>100</b> или <b>0</b> без лимита).",
            reply_markup=build_admin_promo_create_cancel_menu(),
        )
        return

    state_data = await state.get_data()
    max_redemptions = int(raw) or None
    data = NewPromoCodeData(
        code=state_data["promo_code"],
        title=state_data["promo_title"],
        bonus_days=state_data.get("promo_bonus_days", 0),
        is_infinite=state_data.get("promo_is_infinite", False),
        apply_to_all=state_data.get("promo_apply_to_all", True),
        max_redemptions=max_redemptions,
    )

    try:
        promo = await promos.create_promo(data)
    except Exception:
        await state.clear()
        await message.answer(
            "⚠️ Не удалось создать промокод. Возможно, такой код уже существует.",
            reply_markup=build_admin_promo_create_cancel_menu(),
        )
        return

    await state.clear()
    await message.answer(
        "✅ <b>Промокод создан!</b>\n\n" + build_admin_promo_detail_text(promo),
        reply_markup=build_admin_promo_detail_menu(promo),
    )
