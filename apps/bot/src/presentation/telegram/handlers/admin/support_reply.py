# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.support import SupportService
from src.presentation.telegram.callbacks import ADMIN_TICKET_REPLY_PREFIX
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import build_admin_support_reply_cancel_menu
from src.presentation.telegram.keyboards.client import build_support_reply_rating_menu
from src.presentation.telegram.screens.admin import build_admin_support_reply_prompt_text
from src.presentation.telegram.states import AdminSupportReplyState

from .common import answer_access_denied, is_admin_user
from .support_common import parse_ticket_id

router = Router(name="admin_support_reply")


@router.callback_query(F.data.startswith(ADMIN_TICKET_REPLY_PREFIX))
async def admin_ticket_reply_start_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    support: FromDishka[SupportService],
    state: FSMContext,
) -> None:
    if not is_admin_user(settings=settings, telegram_user_id=callback.from_user.id):
        await answer_access_denied(callback)
        return

    ticket_id = parse_ticket_id(callback.data or "", ADMIN_TICKET_REPLY_PREFIX)
    if ticket_id is None:
        await callback.answer("Некорректный идентификатор тикета.", show_alert=True)
        return

    detail = await support.get_ticket_detail(ticket_id)
    if detail is None:
        await callback.answer("Тикет не найден.", show_alert=True)
        return

    await state.update_data(support_ticket_id=str(ticket_id))
    await state.set_state(AdminSupportReplyState.waiting_reply)
    await safe_edit_message(
        callback,
        text=build_admin_support_reply_prompt_text(detail),
        reply_markup=build_admin_support_reply_cancel_menu(ticket_id),
    )
    await callback.answer()


@router.message(AdminSupportReplyState.waiting_reply)
async def admin_ticket_reply_message_handler(
    message: Message,
    settings: FromDishka[Settings],
    support: FromDishka[SupportService],
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

    reply_text = (message.text or "").strip()
    if not reply_text:
        await message.answer("Текст ответа не может быть пустым. Попробуйте ещё раз.")
        return

    state_data = await state.get_data()
    raw_ticket_id = state_data.get("support_ticket_id")
    if not raw_ticket_id:
        await state.clear()
        await message.answer("Не удалось определить тикет. Попробуйте ещё раз.")
        return

    ticket_id = parse_ticket_id(str(raw_ticket_id), "")
    if ticket_id is None:
        await state.clear()
        await message.answer("Некорректный идентификатор тикета.")
        return

    detail = await support.reply_to_ticket(
        ticket_id,
        admin_telegram_id=telegram_user.id,
        text=reply_text,
    )
    await state.clear()

    if detail is None:
        await message.answer("Тикет не найден.")
        return

    try:
        await message.bot.send_message(
            detail.user_telegram_id,
            f"💬 <b>Ответ от поддержки</b>\n\n{reply_text}\n\n<i>Оцени качество ответа:</i>",
            reply_markup=build_support_reply_rating_menu(detail.id),
        )
    except Exception:
        pass

    from src.presentation.telegram.keyboards.admin import build_admin_support_ticket_detail_menu
    from src.presentation.telegram.screens.admin import build_admin_support_ticket_detail_text

    await message.answer(
        "✅ Ответ отправлен пользователю.\n\n" + build_admin_support_ticket_detail_text(detail),
        reply_markup=build_admin_support_ticket_detail_menu(detail),
    )
