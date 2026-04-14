# ruff: noqa: RUF001

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import uuid

from src.application.promos.dto import EligibleVpnAccess, PromoCodeInfo, PromoOverview
from src.presentation.telegram.datetime import format_datetime_msk
from src.presentation.telegram.callbacks import (
    ACTION_PROMO,
    ACTION_REFER,
    ACTION_REVIEW_SKIP,
    ACTION_REVIEWS,
    ACTION_STATUS,
    ACTION_SUPPORT,
    MENU_HOME,
    MENU_PROMO,
    MENU_REVIEWS,
    PROMO_APPLY_PREFIX,
    PROMO_SELECT_ACCESS_PREFIX,
    REVIEW_RATING_PREFIX,
    SUPPORT_RATING_PREFIX,
)


def build_referral_menu(*, referral_link: str | None) -> InlineKeyboardMarkup:
    inline_keyboard = []
    if referral_link is not None:
        inline_keyboard.append(
            [InlineKeyboardButton(text="🔗 Поделиться ссылкой", url=referral_link)]
        )
    inline_keyboard.append(
        [
            InlineKeyboardButton(text="🔄 Обновить", callback_data=ACTION_REFER),
            InlineKeyboardButton(text="🏠 Главная", callback_data=MENU_HOME),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_promo_menu(overview: PromoOverview | None = None) -> InlineKeyboardMarkup:
    rows = []

    if overview:
        for promo in overview.recent_promos:
            rows.append([InlineKeyboardButton(
                text=_promo_button_label(promo),
                callback_data=f"{PROMO_APPLY_PREFIX}{promo.code}",
            )])

    rows.append([
        InlineKeyboardButton(text="✏️ Ввести вручную", callback_data=ACTION_PROMO),
        InlineKeyboardButton(text="🏠 Главная", callback_data=MENU_HOME),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_promo_select_access_menu(
    promo_code: str,
    eligible: tuple[EligibleVpnAccess, ...],
) -> InlineKeyboardMarkup:
    rows = []
    for ea in eligible:
        expires_str = format_datetime_msk(ea.expires_at, include_tz=False)
        label = f"Подписка #{ea.number} · до {expires_str}"
        rows.append([InlineKeyboardButton(
            text=label,
            callback_data=f"{PROMO_SELECT_ACCESS_PREFIX}{promo_code}:{ea.access_id}",
        )])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=MENU_PROMO)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _promo_button_label(promo: PromoCodeInfo) -> str:
    if promo.is_infinite:
        bonus = "♾️"
    elif promo.bonus_days:
        bonus = f"+{promo.bonus_days} дн."
    else:
        bonus = "🎁"

    remaining = (
        f" ({promo.remaining_activations} ост.)"
        if promo.remaining_activations is not None
        else ""
    )
    return f"{bonus} {promo.title}{remaining}"


def build_reviews_menu(*, has_own_review: bool = False) -> InlineKeyboardMarkup:
    review_btn_text = "✏️ Изменить отзыв" if has_own_review else "✍️ Оставить отзыв"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=review_btn_text, callback_data=ACTION_REVIEWS),
                InlineKeyboardButton(text="🏠 Главная", callback_data=MENU_HOME),
            ]
        ]
    )


def build_review_rating_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1 ⭐", callback_data=f"{REVIEW_RATING_PREFIX}1"),
                InlineKeyboardButton(text="2 ⭐", callback_data=f"{REVIEW_RATING_PREFIX}2"),
                InlineKeyboardButton(text="3 ⭐", callback_data=f"{REVIEW_RATING_PREFIX}3"),
                InlineKeyboardButton(text="4 ⭐", callback_data=f"{REVIEW_RATING_PREFIX}4"),
                InlineKeyboardButton(text="5 ⭐", callback_data=f"{REVIEW_RATING_PREFIX}5"),
            ],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=MENU_REVIEWS)],
        ]
    )


def build_review_text_input_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏭ Пропустить", callback_data=ACTION_REVIEW_SKIP),
                InlineKeyboardButton(text="⬅️ Назад", callback_data=MENU_REVIEWS),
            ]
        ]
    )


def build_status_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Обновить", callback_data=ACTION_STATUS),
                InlineKeyboardButton(text="🏠 Главная", callback_data=MENU_HOME),
            ]
        ]
    )


def build_support_menu(*, support_url: str | None) -> InlineKeyboardMarkup:
    inline_keyboard = []
    if support_url is not None:
        inline_keyboard.append(
            [InlineKeyboardButton(text="💬 Открыть канал поддержки", url=support_url)]
        )
    inline_keyboard.append(
        [
            InlineKeyboardButton(text="✉️ Написать", callback_data=ACTION_SUPPORT),
            InlineKeyboardButton(text="🏠 Главная", callback_data=MENU_HOME),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_support_reply_rating_menu(ticket_id: uuid.UUID) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{i} ⭐",
                    callback_data=f"{SUPPORT_RATING_PREFIX}{ticket_id}:{i}",
                )
                for i in range(1, 6)
            ]
        ]
    )


def build_text_input_menu(*, back_callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Отмена", callback_data=back_callback)],
        ]
    )
