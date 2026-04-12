# ruff: noqa: RUF001

from html import escape

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.promos import ApplyPromoCodeUseCase, GetPromoOverviewUseCase
from src.application.referrals import GetReferralOverviewUseCase
from src.application.reviews import CreateReviewUseCase, GetReviewsOverviewUseCase
from src.application.status import GetServiceStatusUseCase
from src.application.support import GetSupportOverviewUseCase
from src.presentation.telegram.callbacks import (
    ACTION_PROMO,
    ACTION_REFER,
    ACTION_REVIEWS,
    ACTION_STATUS,
    ACTION_SUPPORT,
    MENU_PROMO,
    MENU_REFER,
    MENU_REVIEWS,
    MENU_STATUS,
    MENU_SUPPORT,
    REVIEW_RATING_PREFIX,
)
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.client import (
    build_promo_menu,
    build_referral_menu,
    build_review_rating_menu,
    build_reviews_menu,
    build_status_menu,
    build_support_menu,
    build_text_input_menu,
)
from src.presentation.telegram.screens.client import (
    build_promo_input_text,
    build_promo_result_text,
    build_promo_text,
    build_referral_text,
    build_review_rating_text,
    build_review_text_prompt,
    build_reviews_text,
    build_status_text,
    build_support_prompt_text,
    build_support_text,
)
from src.presentation.telegram.states import PromoCodeState, ReviewState, SupportState

router = Router(name="client")


def parse_review_rating(data: str | None) -> int | None:
    if data is None or not data.startswith(REVIEW_RATING_PREFIX):
        return None

    raw_value = data.removeprefix(REVIEW_RATING_PREFIX)
    if raw_value not in {"1", "2", "3", "4", "5"}:
        return None

    return int(raw_value)


async def resolve_bot_username(bot: Bot, settings: Settings) -> str | None:
    if settings.bot_public_username:
        return settings.bot_public_username.removeprefix("@")

    me = await bot.get_me()
    return me.username


def build_referral_link(*, bot_username: str | None, referral_code: str) -> str | None:
    if not bot_username:
        return None
    return f"https://t.me/{bot_username}?start=ref_{referral_code}"


@router.callback_query(F.data == MENU_REFER)
@router.callback_query(F.data == ACTION_REFER)
async def referral_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    get_referral_overview: FromDishka[GetReferralOverviewUseCase],
    state: FSMContext,
) -> None:
    overview = await get_referral_overview.execute(callback.from_user.id)
    if overview is None:
        await callback.answer(
            "Профиль пока не найден. Отправьте /start ещё раз.",
            show_alert=True,
        )
        return

    bot_username = await resolve_bot_username(callback.bot, settings)
    await state.clear()
    await safe_edit_message(
        callback,
        text=build_referral_text(overview),
        reply_markup=build_referral_menu(
            referral_link=build_referral_link(
                bot_username=bot_username,
                referral_code=overview.referral_code,
            )
        ),
    )
    await callback.answer("Реферальный кабинет обновлён ✨")


@router.callback_query(F.data == MENU_PROMO)
async def promo_section_callback_handler(
    callback: CallbackQuery,
    get_promo_overview: FromDishka[GetPromoOverviewUseCase],
    state: FSMContext,
) -> None:
    overview = await get_promo_overview.execute(callback.from_user.id)
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
        reply_markup=build_promo_menu(),
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
    await callback.answer("Жду промокод ✨")


@router.message(PromoCodeState.waiting_code)
async def promo_message_handler(
    message: Message,
    apply_promo_code: FromDishka[ApplyPromoCodeUseCase],
    state: FSMContext,
) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        await state.clear()
        await message.answer("Не удалось определить профиль. Отправьте /start ещё раз.")
        return

    try:
        result = await apply_promo_code.execute(
            telegram_user.id,
            code=message.text or "",
        )
    except ValueError as exc:
        await message.answer(str(exc))
        return

    await state.clear()
    await message.answer(
        build_promo_result_text(result),
        reply_markup=build_promo_menu(),
    )


@router.callback_query(F.data == MENU_REVIEWS)
async def reviews_section_callback_handler(
    callback: CallbackQuery,
    get_reviews_overview: FromDishka[GetReviewsOverviewUseCase],
    state: FSMContext,
) -> None:
    overview = await get_reviews_overview.execute()
    await state.clear()
    await safe_edit_message(
        callback,
        text=build_reviews_text(overview),
        reply_markup=build_reviews_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == ACTION_REVIEWS)
async def review_action_callback_handler(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.clear()
    await safe_edit_message(
        callback,
        text=build_review_rating_text(),
        reply_markup=build_review_rating_menu(),
    )
    await callback.answer("Выберите оценку ⭐")


@router.callback_query(F.data.startswith(REVIEW_RATING_PREFIX))
async def review_rating_callback_handler(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    rating = parse_review_rating(callback.data)
    if rating is None:
        await callback.answer("Не удалось определить оценку.", show_alert=True)
        return

    await state.update_data(review_rating=rating)
    await state.set_state(ReviewState.waiting_text)
    await safe_edit_message(
        callback,
        text=build_review_text_prompt(rating),
        reply_markup=build_text_input_menu(back_callback=MENU_REVIEWS),
    )
    await callback.answer("Теперь напишите пару слов ✍️")


@router.message(ReviewState.waiting_text)
async def review_message_handler(
    message: Message,
    create_review: FromDishka[CreateReviewUseCase],
    get_reviews_overview: FromDishka[GetReviewsOverviewUseCase],
    state: FSMContext,
) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        await state.clear()
        await message.answer("Не удалось определить профиль. Отправьте /start ещё раз.")
        return

    state_data = await state.get_data()
    rating = state_data.get("review_rating")
    if not isinstance(rating, int):
        await state.clear()
        await message.answer(
            "Не удалось определить оценку. Попробуйте ещё раз через раздел отзывов.",
        )
        return

    try:
        is_created = await create_review.execute(
            telegram_user.id,
            rating=rating,
            text=message.text or "",
        )
    except ValueError as exc:
        await message.answer(str(exc))
        return

    await state.clear()
    if not is_created:
        await message.answer("Профиль пока не найден. Отправьте /start ещё раз.")
        return

    overview = await get_reviews_overview.execute()
    await message.answer(
        "Спасибо за отзыв 💙\n\nОн уже появился в ленте ниже.",
        reply_markup=build_reviews_menu(),
    )
    await message.answer(
        build_reviews_text(overview),
        reply_markup=build_reviews_menu(),
    )


@router.callback_query(F.data == MENU_STATUS)
@router.callback_query(F.data == ACTION_STATUS)
async def status_callback_handler(
    callback: CallbackQuery,
    get_service_status: FromDishka[GetServiceStatusUseCase],
    state: FSMContext,
) -> None:
    overview = await get_service_status.execute()
    await state.clear()
    await safe_edit_message(
        callback,
        text=build_status_text(overview),
        reply_markup=build_status_menu(),
    )
    await callback.answer("Статус обновлён ✨")


@router.callback_query(F.data == MENU_SUPPORT)
async def support_section_callback_handler(
    callback: CallbackQuery,
    get_support_overview: FromDishka[GetSupportOverviewUseCase],
    state: FSMContext,
) -> None:
    overview = await get_support_overview.execute()
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
    await callback.answer("Жду ваше сообщение 💬")


@router.message(SupportState.waiting_message)
async def support_message_handler(
    message: Message,
    settings: FromDishka[Settings],
    get_support_overview: FromDishka[GetSupportOverviewUseCase],
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
    support_overview = await get_support_overview.execute()

    forwarded_count = 0
    username_text = f"@{telegram_user.username}" if telegram_user.username else "без username"
    for admin_id in settings.admin_ids:
        try:
            await message.bot.send_message(
                admin_id,
                (
                    "🆘 <b>Новое сообщение в поддержку</b>\n\n"
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
        "Сообщение отправлено в поддержку 🛟\n\nМы вернёмся к вам, как только увидим запрос.",
        reply_markup=build_support_menu(support_url=support_overview.support_url),
    )
