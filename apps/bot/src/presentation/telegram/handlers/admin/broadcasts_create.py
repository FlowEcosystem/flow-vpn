# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.broadcasts import BroadcastsService
from src.infrastructure.database import Database
from src.presentation.telegram.callbacks import (
    ACTION_ADMIN_BROADCASTS,
    ACTION_ADMIN_BROADCASTS_CONFIRM,
    BROADCAST_SEGMENT_PREFIX,
)
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import (
    build_admin_broadcast_confirm_menu,
    build_admin_broadcast_segment_menu,
    build_admin_broadcast_text_cancel_menu,
    build_admin_broadcasts_menu,
)
from src.presentation.telegram.screens.admin import (
    build_admin_broadcast_launched_text,
    build_admin_broadcast_preview_text,
    build_admin_broadcast_segment_text,
    build_admin_broadcast_text_prompt,
    format_segment_label,
)
from src.presentation.telegram.states import AdminBroadcastCreationState

from .broadcasts_runtime import spawn_broadcast_task
from .common import answer_access_denied, is_admin_user

router = Router(name="admin_broadcasts_create")


@router.callback_query(F.data == ACTION_ADMIN_BROADCASTS)
async def admin_broadcast_create_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    state: FSMContext,
) -> None:
    if not is_admin_user(settings=settings, telegram_user_id=callback.from_user.id):
        await answer_access_denied(callback)
        return

    await state.clear()
    await safe_edit_message(
        callback,
        text=build_admin_broadcast_segment_text(),
        reply_markup=build_admin_broadcast_segment_menu(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(BROADCAST_SEGMENT_PREFIX))
async def admin_broadcast_segment_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    state: FSMContext,
) -> None:
    if not is_admin_user(settings=settings, telegram_user_id=callback.from_user.id):
        await answer_access_denied(callback)
        return

    segment = (callback.data or "").removeprefix(BROADCAST_SEGMENT_PREFIX)
    if segment not in ("all", "with_access", "without_access"):
        await callback.answer("Неверный сегмент.", show_alert=True)
        return

    await state.update_data(broadcast_segment=segment)
    await state.set_state(AdminBroadcastCreationState.waiting_text)
    segment_label = format_segment_label(segment)
    await safe_edit_message(
        callback,
        text=build_admin_broadcast_text_prompt(segment_label),
        reply_markup=build_admin_broadcast_text_cancel_menu(),
    )
    await callback.answer()


@router.message(AdminBroadcastCreationState.waiting_text)
async def admin_broadcast_text_message_handler(
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

    text = (message.text or "").strip()
    if not text:
        await message.answer(
            "Текст не может быть пустым.",
            reply_markup=build_admin_broadcast_text_cancel_menu(),
        )
        return

    state_data = await state.get_data()
    segment = state_data.get("broadcast_segment", "all")
    segment_label = format_segment_label(segment)

    await state.update_data(broadcast_text=text)
    await state.set_state(AdminBroadcastCreationState.waiting_confirm)

    await message.answer(
        build_admin_broadcast_preview_text(segment_label, text),
        reply_markup=build_admin_broadcast_confirm_menu(),
    )


@router.callback_query(
    AdminBroadcastCreationState.waiting_confirm,
    F.data == ACTION_ADMIN_BROADCASTS_CONFIRM,
)
async def admin_broadcast_confirm_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    broadcasts_service: FromDishka[BroadcastsService],
    database: FromDishka[Database],
    state: FSMContext,
) -> None:
    if not is_admin_user(settings=settings, telegram_user_id=callback.from_user.id):
        await answer_access_denied(callback)
        return

    state_data = await state.get_data()
    segment = state_data.get("broadcast_segment", "all")
    text = state_data.get("broadcast_text", "")

    if not text:
        await state.clear()
        await callback.answer("Текст рассылки не найден. Начните заново.", show_alert=True)
        return

    await state.clear()

    summary, telegram_ids = await broadcasts_service.create(
        text=text,
        target_segment=segment,
    )

    segment_label = format_segment_label(segment)
    await safe_edit_message(
        callback,
        text=build_admin_broadcast_launched_text(segment_label, len(telegram_ids)),
        reply_markup=build_admin_broadcasts_menu(()),
    )
    await callback.answer("Рассылка запущена 📢")

    message = callback.message
    if isinstance(message, Message):
        spawn_broadcast_task(
            summary_id=summary.id,
            text=text,
            telegram_ids=telegram_ids,
            message=message,
            database=database,
        )
