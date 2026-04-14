# ruff: noqa: RUF001

from html import escape
from uuid import UUID

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.support import SupportService
from src.presentation.telegram.callbacks import ACTION_SUPPORT, MENU_SUPPORT, SUPPORT_RATING_PREFIX
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.client import (
    build_support_menu,
    build_support_reply_rating_menu,
    build_text_input_menu,
)
from src.presentation.telegram.screens.client import build_support_prompt_text, build_support_text
from src.presentation.telegram.states import SupportState

router = Router(name="client_support")


@router.callback_query(F.data == MENU_SUPPORT)
async def support_section_callback_handler(
    callback: CallbackQuery,
    support: FromDishka[SupportService],
    state: FSMContext,
) -> None:
    overview = await support.get_overview()
    await state.clear()
    await safe_edit_message(
        callback,
        text=build_support_text(overview),
        reply_markup=build_support_menu(support_url=overview.support_url),
    )
    await callback.answer()


@router.callback_query(F.data == ACTION_SUPPORT)
async def support_action_callback_handler(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.set_state(SupportState.waiting_message)
    await safe_edit_message(
        callback,
        text=build_support_prompt_text(),
        reply_markup=build_text_input_menu(back_callback=MENU_SUPPORT),
    )
    await callback.answer()


@router.message(SupportState.waiting_message)
async def support_message_handler(
    message: Message,
    settings: FromDishka[Settings],
    support: FromDishka[SupportService],
    state: FSMContext,
) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        await state.clear()
        await message.answer("Не удалось определить профиль. Отправьте /start ещё раз.")
        return

    text = (message.text or "").strip()
    if len(text) < 6:
        await message.answer("Опишите вопрос чуть подробнее, чтобы мы смогли помочь.")
        return

    await state.clear()
    support_overview = await support.get_overview()
    ticket_id = await support.create_ticket(telegram_user.id, message=text)

    forwarded_count = 0
    username_text = f"@{telegram_user.username}" if telegram_user.username else "без username"
    ticket_ref = f" · тикет #{str(ticket_id)[:8]}" if ticket_id else ""
    for admin_id in settings.admin_ids:
        try:
            await message.bot.send_message(
                admin_id,
                (
                    f"🆘 <b>Новое обращение в поддержку{ticket_ref}</b>\n\n"
                    f"• Пользователь: <b>{escape(telegram_user.full_name)}</b>\n"
                    f"• Telegram ID: <code>{telegram_user.id}</code>\n"
                    f"• Username: <b>{escape(username_text)}</b>\n\n"
                    f"{escape(text)}"
                ),
            )
        except Exception:
            continue
        forwarded_count += 1

    if forwarded_count == 0 and support_overview.support_url is None:
        await message.answer(
            "Сейчас не удалось передать сообщение команде. Попробуйте позже.",
            reply_markup=build_support_menu(support_url=support_overview.support_url),
        )
        return

    await message.answer(
        "Обращение принято 🛟\n\nМы ответим, как только увидим запрос.",
        reply_markup=build_support_menu(support_url=support_overview.support_url),
    )


@router.callback_query(F.data.startswith(SUPPORT_RATING_PREFIX))
async def support_rating_callback_handler(
    callback: CallbackQuery,
    support: FromDishka[SupportService],
) -> None:
    raw = (callback.data or "").removeprefix(SUPPORT_RATING_PREFIX)
    parts = raw.rsplit(":", 1)
    if len(parts) != 2:
        await callback.answer("Некорректные данные.", show_alert=True)
        return

    try:
        ticket_id = UUID(parts[0])
        rating = int(parts[1])
    except (ValueError, IndexError):
        await callback.answer("Некорректные данные.", show_alert=True)
        return

    if rating not in range(1, 6):
        await callback.answer("Некорректная оценка.", show_alert=True)
        return

    rated = await support.rate_ticket(callback.from_user.id, ticket_id, rating)
    if not rated:
        await callback.answer("Оценка уже поставлена или обращение не найдено.", show_alert=True)
        return

    stars = "⭐" * rating
    await callback.answer(f"Спасибо за оценку! {stars}", show_alert=False)

    message = callback.message
    if isinstance(message, Message):
        try:
            await message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
