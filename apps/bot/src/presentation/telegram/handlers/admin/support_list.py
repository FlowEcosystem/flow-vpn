# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.support import SupportService
from src.presentation.telegram.callbacks import ADMIN_TICKET_VIEW_PREFIX, MENU_ADMIN_SUPPORT
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import (
    build_admin_support_ticket_detail_menu,
    build_admin_support_tickets_menu,
)
from src.presentation.telegram.screens.admin import (
    build_admin_support_ticket_detail_text,
    build_admin_support_tickets_text,
)

from .common import answer_access_denied, is_admin_user
from .support_common import parse_ticket_id

router = Router(name="admin_support_list")


@router.callback_query(F.data == MENU_ADMIN_SUPPORT)
async def admin_support_tickets_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    support: FromDishka[SupportService],
    state: FSMContext,
) -> None:
    if not is_admin_user(settings=settings, telegram_user_id=callback.from_user.id):
        await answer_access_denied(callback)
        return

    await state.clear()
    tickets = await support.list_open_tickets()
    await safe_edit_message(
        callback,
        text=build_admin_support_tickets_text(tickets),
        reply_markup=build_admin_support_tickets_menu(tickets),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(ADMIN_TICKET_VIEW_PREFIX))
async def admin_ticket_view_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    support: FromDishka[SupportService],
    state: FSMContext,
) -> None:
    if not is_admin_user(settings=settings, telegram_user_id=callback.from_user.id):
        await answer_access_denied(callback)
        return

    ticket_id = parse_ticket_id(callback.data or "", ADMIN_TICKET_VIEW_PREFIX)
    if ticket_id is None:
        await callback.answer("Некорректный идентификатор тикета.", show_alert=True)
        return

    detail = await support.get_ticket_detail(ticket_id)
    if detail is None:
        await callback.answer("Тикет не найден.", show_alert=True)
        return

    await state.clear()
    await safe_edit_message(
        callback,
        text=build_admin_support_ticket_detail_text(detail),
        reply_markup=build_admin_support_ticket_detail_menu(detail),
    )
    await callback.answer()
