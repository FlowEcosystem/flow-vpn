# ruff: noqa: RUF001

from html import escape

from src.application.promos import (
    EligibleVpnAccess,
    PromoActivationResult,
    PromoActivationStatus,
    PromoCodeInfo,
    PromoOverview,
)
from src.application.referrals import ReferralInvitee, ReferralOverview
from src.application.reviews import PublicReview, ReviewsOverview
from src.application.status import ServiceStatusLevel, ServiceStatusOverview
from src.application.support import SupportOverview
from src.presentation.telegram.datetime import format_datetime_msk


def build_referral_text(overview: ReferralOverview) -> str:
    if overview.recent_referrals:
        invitees_lines = "\n".join(
            _format_referral_line(item) for item in overview.recent_referrals
        )
        invitees_block = f"\n{invitees_lines}"
    else:
        invitees_block = "\nПока никого нет — поделись ссылкой первым."

    return (
        "🎁 <b>Рефералы</b>\n\n"
        f"✅ Зачтено: <b>{overview.activated_referrals}</b>  "
        f"·  ⏳ Ожидают: <b>{overview.pending_referrals}</b>\n"
        f"Твой код: <code>{overview.referral_code}</code>\n\n"
        f"Переходы по ссылке:{invitees_block}"
    )


def build_promo_text(overview: PromoOverview) -> str:
    if overview.recent_promos:
        promos_note = f"Доступно промокодов: <b>{len(overview.recent_promos)}</b> — нажми кнопку ниже."
    else:
        promos_note = "Публичных промокодов сейчас нет.\nЕсли у тебя есть код — введи вручную."

    activated_line = (
        f"Активировано тобой: <b>{overview.total_activations}</b>\n\n"
        if overview.total_activations
        else ""
    )
    return (
        "🏷 <b>Промокоды</b>\n\n"
        f"{activated_line}"
        f"{promos_note}"
    )


def build_promo_select_access_text(
    promo: PromoCodeInfo,
    eligible: tuple[EligibleVpnAccess, ...],
) -> str:
    if promo.is_infinite:
        bonus_line = "♾️ Бессрочная подписка"
    else:
        bonus_line = f"📅 +{promo.bonus_days} дней"

    return (
        f"🏷 <b>{escape(promo.title)}</b> · {bonus_line}\n\n"
        f"У тебя несколько подписок — к какой применить?\n"
        f"<i>Выбери одну из кнопок ниже.</i>"
    )


def build_promo_input_text() -> str:
    return (
        "✏️ <b>Введи промокод</b>\n\n"
        "Отправь код одним сообщением.\n"
        "Например: <code>FLOW30</code>"
    )


def build_promo_result_text(result: PromoActivationResult) -> str:
    if result.status is PromoActivationStatus.APPLIED and result.promo is not None:
        if result.promo.is_infinite:
            bonus_line = "♾️ Подписка стала бессрочной\n\n"
        elif result.promo.bonus_days > 0:
            bonus_line = f"📅 +{result.promo.bonus_days} дней к подписке\n\n"
        else:
            bonus_line = ""
        scope = "ко всем подпискам" if result.promo.apply_to_all else "к выбранной подписке"
        scope_line = f"<i>Применено {scope}</i>" if bonus_line else ""
        return (
            f"✅ <b>{escape(result.promo.title)}</b>\n\n"
            f"{bonus_line}{scope_line}"
        ).rstrip()

    if result.status is PromoActivationStatus.NO_ELIGIBLE_ACCESSES:
        return (
            "⚠️ <b>Промокод не применён</b>\n\n"
            f"{escape(result.message)}"
        )

    return (
        f"❌ <b>Не получилось</b>\n\n"
        f"{escape(result.message)}"
    )


def build_reviews_text(overview: ReviewsOverview) -> str:
    if overview.total_reviews:
        rating_line = f"⭐ <b>{overview.average_rating:.1f}</b> · {overview.total_reviews} отзывов"
    else:
        rating_line = "Отзывов пока нет"

    own_block = ""
    if overview.user_review is not None:
        own_block = f"\n\n<b>Твой отзыв:</b>\n{_format_review_line(overview.user_review)}"

    other_reviews = [r for r in overview.recent_reviews if not r.is_own]
    if other_reviews:
        reviews_lines = "\n\n".join(_format_review_line(r) for r in other_reviews)
        community_block = f"\n\n{reviews_lines}"
    elif not overview.user_review:
        community_block = "\n\nБудь первым — оставь отзыв."
    else:
        community_block = ""

    return f"💬 <b>Отзывы</b>\n\n{rating_line}{own_block}{community_block}"


def build_review_rating_text(*, is_edit: bool = False, current_rating: int | None = None) -> str:
    if is_edit and current_rating is not None:
        stars = "⭐" * current_rating
        return (
            f"✏️ <b>Изменить отзыв</b>\n\n"
            f"Текущая оценка: {stars}\n\n"
            "Выбери новую оценку:"
        )

    return "⭐ <b>Новый отзыв</b>\n\nВыбери оценку:"


def build_review_text_prompt(rating: int, *, is_edit: bool = False) -> str:
    stars = "⭐" * rating
    action = "Изменить отзыв" if is_edit else "Новый отзыв"
    return (
        f"✍️ <b>{action}</b>\n\n"
        f"{stars}\n\n"
        "Напиши пару слов или нажми «Пропустить»."
    )


def build_review_submitted_text(rating: int, *, is_edit: bool = False) -> str:
    stars = "⭐" * rating
    action = "обновлён" if is_edit else "опубликован"
    return f"✅ <b>Отзыв {action}!</b>  {stars}"


def build_status_text(status: ServiceStatusOverview) -> str:
    checked_at = format_datetime_msk(status.checked_at)
    if status.level is ServiceStatusLevel.ONLINE:
        return (
            "📡 <b>Статус сервисов</b>\n\n"
            "✅ Всё работает штатно\n\n"
            f"Обновлено: {checked_at}"
        )

    return (
        "📡 <b>Статус сервисов</b>\n\n"
        "⚠️ Возможны перебои\n"
        "Уже разбираемся.\n\n"
        f"Обновлено: {checked_at}"
    )


def build_support_text(overview: SupportOverview) -> str:
    channel_line = (
        f"\n💬 <b>{overview.support_title}</b> — наш канал поддержки"
        if overview.support_url and overview.support_title
        else ""
    )

    stats_parts = []
    if overview.closed_tickets_count > 0:
        stats_parts.append(f"✅ Закрыто обращений: <b>{overview.closed_tickets_count}</b>")
    if overview.average_support_rating is not None:
        stars = "⭐" * round(overview.average_support_rating)
        stats_parts.append(
            f"{stars} <b>{overview.average_support_rating:.1f}</b>"
            f" · {overview.total_support_ratings} оценок"
        )
    stats_line = "\n" + "\n".join(stats_parts) if stats_parts else ""

    return (
        f"🛟 <b>Поддержка</b>\n\n"
        f"Поможем с подключением, настройкой или любым вопросом."
        f"{channel_line}{stats_line}"
    )


def build_support_prompt_text() -> str:
    return (
        "✉️ <b>Напиши вопрос</b>\n\n"
        "Опиши проблему одним сообщением."
    )


def _format_referral_line(item: ReferralInvitee) -> str:
    name = item.first_name or (f"@{item.username}" if item.username else "Участник")
    date = format_datetime_msk(item.created_at)
    status = "✅" if item.has_activated_vpn else "⏳"
    return f"{status} <b>{escape(name)}</b> · {date}"




def _format_review_line(review: PublicReview) -> str:
    if review.first_name:
        name = review.first_name
    elif review.username:
        name = f"@{review.username}"
    else:
        name = "Пользователь"

    date = format_datetime_msk(review.created_at)
    stars = "⭐" * review.rating
    text_part = f"\n{escape(review.text)}" if review.text else ""
    return f"<b>{escape(name)}</b> · {stars} · {date}{text_part}"
