# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.application.reviews import ReviewsService
from src.presentation.telegram.callbacks import ACTION_REVIEW_SKIP, ACTION_REVIEWS, MENU_REVIEWS, REVIEW_RATING_PREFIX
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.client import (
    build_review_rating_menu,
    build_review_text_input_menu,
    build_reviews_menu,
)
from src.presentation.telegram.screens.client import (
    build_review_rating_text,
    build_review_submitted_text,
    build_review_text_prompt,
    build_reviews_text,
)
from src.presentation.telegram.states import ReviewState

router = Router(name="client_reviews")


def parse_review_rating(data: str | None) -> int | None:
    if data is None or not data.startswith(REVIEW_RATING_PREFIX):
        return None
    raw_value = data.removeprefix(REVIEW_RATING_PREFIX)
    if raw_value not in {"1", "2", "3", "4", "5"}:
        return None
    return int(raw_value)


@router.callback_query(F.data == MENU_REVIEWS)
async def reviews_section_callback_handler(
    callback: CallbackQuery,
    reviews: FromDishka[ReviewsService],
    state: FSMContext,
) -> None:
    overview = await reviews.get_overview(callback.from_user.id)
    await state.clear()
    await safe_edit_message(
        callback,
        text=build_reviews_text(overview),
        reply_markup=build_reviews_menu(has_own_review=overview.user_review is not None),
    )
    await callback.answer()


@router.callback_query(F.data == ACTION_REVIEWS)
async def review_action_callback_handler(
    callback: CallbackQuery,
    reviews: FromDishka[ReviewsService],
    state: FSMContext,
) -> None:
    overview = await reviews.get_overview(callback.from_user.id)
    is_edit = overview.user_review is not None
    current_rating = overview.user_review.rating if overview.user_review else None

    await state.clear()
    await state.update_data(review_is_edit=is_edit)
    await safe_edit_message(
        callback,
        text=build_review_rating_text(is_edit=is_edit, current_rating=current_rating),
        reply_markup=build_review_rating_menu(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(REVIEW_RATING_PREFIX))
async def review_rating_callback_handler(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    rating = parse_review_rating(callback.data)
    if rating is None:
        await callback.answer("Не удалось определить оценку.", show_alert=True)
        return

    state_data = await state.get_data()
    is_edit = state_data.get("review_is_edit", False)

    await state.update_data(review_rating=rating)
    await state.set_state(ReviewState.waiting_text)
    await safe_edit_message(
        callback,
        text=build_review_text_prompt(rating, is_edit=is_edit),
        reply_markup=build_review_text_input_menu(),
    )
    await callback.answer()


@router.message(ReviewState.waiting_text)
async def review_message_handler(
    message: Message,
    reviews: FromDishka[ReviewsService],
    state: FSMContext,
) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        await state.clear()
        await message.answer("Не удалось определить профиль. Отправьте /start ещё раз.")
        return

    state_data = await state.get_data()
    rating = state_data.get("review_rating")
    is_edit = state_data.get("review_is_edit", False)

    if not isinstance(rating, int):
        await state.clear()
        await message.answer(
            "Не удалось определить оценку. Попробуйте ещё раз через раздел отзывов."
        )
        return

    try:
        is_created = await reviews.create(
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

    await _finish_review_flow(message, reviews, telegram_user.id, rating, is_edit=is_edit)


@router.callback_query(F.data == ACTION_REVIEW_SKIP)
async def review_skip_callback_handler(
    callback: CallbackQuery,
    reviews: FromDishka[ReviewsService],
    state: FSMContext,
) -> None:
    state_data = await state.get_data()
    rating = state_data.get("review_rating")
    is_edit = state_data.get("review_is_edit", False)

    if not isinstance(rating, int):
        await state.clear()
        await callback.answer("Сначала выберите оценку.", show_alert=True)
        return

    await callback.answer()
    is_created = await reviews.create(
        callback.from_user.id,
        rating=rating,
        text="",
    )
    await state.clear()

    if not is_created:
        await callback.answer("Профиль пока не найден. Отправьте /start ещё раз.", show_alert=True)
        return

    overview = await reviews.get_overview(callback.from_user.id)
    await safe_edit_message(
        callback,
        text=(
            build_review_submitted_text(rating, is_edit=is_edit)
            + "\n\n"
            + build_reviews_text(overview)
        ),
        reply_markup=build_reviews_menu(has_own_review=True),
    )


async def _finish_review_flow(
    message: Message,
    reviews: ReviewsService,
    telegram_id: int,
    rating: int,
    *,
    is_edit: bool,
) -> None:
    overview = await reviews.get_overview(telegram_id)
    await message.answer(
        build_review_submitted_text(rating, is_edit=is_edit)
        + "\n\n"
        + build_reviews_text(overview),
        reply_markup=build_reviews_menu(has_own_review=True),
    )
