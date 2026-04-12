# ruff: noqa: RUF001

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.presentation.telegram.callbacks import (
    ACTION_PROMO,
    ACTION_REFER,
    ACTION_REVIEWS,
    ACTION_STATUS,
    ACTION_SUPPORT,
    MENU_HOME,
    MENU_REVIEWS,
    REVIEW_RATING_PREFIX,
)


def build_referral_menu(*, referral_link: str | None) -> InlineKeyboardMarkup:
    inline_keyboard = []
    if referral_link is not None:
        inline_keyboard.append(
            [InlineKeyboardButton(text="🔗 Поделиться ссылкой", url=referral_link)]
        )
    inline_keyboard.extend(
        [
            [InlineKeyboardButton(text="🔄 Обновить статистику", callback_data=ACTION_REFER)],
            [InlineKeyboardButton(text="⬅️ На главную", callback_data=MENU_HOME)],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_promo_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✨ Активировать промокод", callback_data=ACTION_PROMO)],
            [InlineKeyboardButton(text="⬅️ На главную", callback_data=MENU_HOME)],
        ]
    )


def build_reviews_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Оставить отзыв", callback_data=ACTION_REVIEWS)],
            [InlineKeyboardButton(text="⬅️ На главную", callback_data=MENU_HOME)],
        ]
    )


def build_review_rating_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐", callback_data=f"{REVIEW_RATING_PREFIX}1"),
                InlineKeyboardButton(text="⭐⭐", callback_data=f"{REVIEW_RATING_PREFIX}2"),
                InlineKeyboardButton(text="⭐⭐⭐", callback_data=f"{REVIEW_RATING_PREFIX}3"),
            ],
            [
                InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data=f"{REVIEW_RATING_PREFIX}4"),
                InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data=f"{REVIEW_RATING_PREFIX}5"),
            ],
            [InlineKeyboardButton(text="⬅️ К отзывам", callback_data=MENU_REVIEWS)],
        ]
    )


def build_status_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Обновить статус", callback_data=ACTION_STATUS)],
            [InlineKeyboardButton(text="⬅️ На главную", callback_data=MENU_HOME)],
        ]
    )


def build_support_menu(*, support_url: str | None) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton(text="💬 Написать в поддержку", callback_data=ACTION_SUPPORT)]
    ]
    if support_url is not None:
        inline_keyboard.append(
            [InlineKeyboardButton(text="🔗 Открыть канал поддержки", url=support_url)]
        )
    inline_keyboard.append(
        [InlineKeyboardButton(text="⬅️ На главную", callback_data=MENU_HOME)]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_text_input_menu(*, back_callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback)],
        ]
    )
