# ruff: noqa: RUF001

from datetime import UTC
from html import escape

from src.application.promos import (
    PromoActivationResult,
    PromoActivationStatus,
    PromoCodeInfo,
    PromoOverview,
)
from src.application.referrals import ReferralInvitee, ReferralOverview
from src.application.reviews import PublicReview, ReviewsOverview
from src.application.status import ServiceStatusLevel, ServiceStatusOverview
from src.application.support import SupportOverview


def build_referral_text(overview: ReferralOverview) -> str:
    recent_referrals_block = (
        "\n".join(_format_referral_line(item) for item in overview.recent_referrals)
        if overview.recent_referrals
        else "• Пока приглашений нет — отправьте ссылку друзьям и заберите первый бонус ✨"
    )
    return (
        "🎁 <b>Рефералы</b>\n\n"
        "Приглашайте друзей в Flow VPN и получайте приятные бонусы за каждое подключение.\n\n"
        f"• Приглашено друзей: <b>{overview.total_referrals}</b>\n"
        f"• Ваш код: <code>{overview.referral_code}</code>\n\n"
        "Последние подключения:\n"
        f"{recent_referrals_block}\n\n"
        "Поделитесь ссылкой ниже — бот сам учтёт переход по вашему приглашению."
    )


def build_promo_text(overview: PromoOverview) -> str:
    recent_promos_block = (
        "\n".join(_format_promo_line(promo) for promo in overview.recent_promos)
        if overview.recent_promos
        else "• Сейчас активных публичных промокодов нет"
    )
    return (
        "🏷 <b>Промокоды</b>\n\n"
        "Здесь можно активировать бонусный код и сохранить его в своём аккаунте.\n\n"
        f"• Уже активировано кодов: <b>{overview.total_activations}</b>\n\n"
        "Что доступно сейчас:\n"
        f"{recent_promos_block}\n\n"
        "Если код уже есть на руках, нажмите кнопку ниже и отправьте его сообщением."
    )


def build_promo_input_text() -> str:
    return (
        "✨ <b>Активация промокода</b>\n\n"
        "Отправьте промокод одним сообщением.\n"
        "Например: <code>FLOW30</code>\n\n"
        "Я сразу проверю его и применю к вашему аккаунту."
    )


def build_promo_result_text(result: PromoActivationResult) -> str:
    if result.status is PromoActivationStatus.APPLIED and result.promo is not None:
        bonus = (
            f"• Бонус: <b>+{result.promo.bonus_days} дней</b>\n"
            if result.promo.bonus_days > 0
            else ""
        )
    return (
        "✅ <b>Промокод активирован</b>\n\n"
            f"<b>{escape(result.promo.title)}</b>\n"
            f"{bonus}"
            f"{escape(result.message)}\n\n"
            "Бонус уже сохранён за вашим аккаунтом ✨"
        )

    return (
        "⚠️ <b>Промокод не применён</b>\n\n"
        f"{escape(result.message)}\n\n"
        "Проверьте написание кода и попробуйте ещё раз."
    )


def build_reviews_text(overview: ReviewsOverview) -> str:
    recent_reviews_block = (
        "\n\n".join(_format_review_line(review) for review in overview.recent_reviews)
        if overview.recent_reviews
        else "Пока отзывов немного — можно стать первым и задать тон ✨"
    )
    average_rating = f"{overview.average_rating:.1f}" if overview.total_reviews else "—"
    return (
        "💬 <b>Отзывы</b>\n\n"
        "Здесь собраны живые впечатления пользователей о Flow VPN.\n\n"
        f"• Средняя оценка: <b>{average_rating}</b>\n"
        f"• Всего отзывов: <b>{overview.total_reviews}</b>\n\n"
        f"{recent_reviews_block}\n\n"
        "Если уже пользуетесь сервисом, поделитесь своим опытом —\n"
        "это помогает делать продукт лучше."
    )


def build_review_rating_text() -> str:
    return (
        "⭐ <b>Новый отзыв</b>\n\n"
        "Сначала выберите оценку от 1 до 5.\n"
        "После этого я попрошу коротко описать впечатление."
    )


def build_review_text_prompt(rating: int) -> str:
    return (
        "✍️ <b>Поделитесь впечатлением</b>\n\n"
        f"Оценка: <b>{'⭐' * rating}</b>\n\n"
        "Напишите пару слов о скорости, стабильности или общем опыте.\n"
        "Короткий живой отзыв уже отлично подойдёт."
    )


def build_status_text(status: ServiceStatusOverview) -> str:
    checked_at = status.checked_at.astimezone(UTC).strftime("%d.%m.%Y %H:%M UTC")
    if status.level is ServiceStatusLevel.ONLINE:
        return (
            "📡 <b>Статус сервиса</b>\n\n"
            "Сейчас всё выглядит стабильно:\n"
            "точки подключения доступны, сервис отвечает штатно ✅\n\n"
            f"Последняя проверка: <b>{checked_at}</b>\n\n"
            "Если что-то изменится, этот экран обновится первым."
        )

    return (
        "📡 <b>Статус сервиса</b>\n\n"
        "Сейчас мы видим, что часть инфраструктуры отвечает нестабильно.\n"
        "Команда уже проверяет ситуацию 🛠\n\n"
        f"Последняя проверка: <b>{checked_at}</b>\n\n"
        "Если подключение не открывается, попробуйте обновить статус чуть позже."
    )


def build_support_text(overview: SupportOverview) -> str:
    support_line = (
        f"• Канал связи: <b>{overview.support_title}</b>\n\n"
        if overview.support_url
        else ""
    )
    return (
        "🛟 <b>Поддержка</b>\n\n"
        "Если что-то пошло не так с подключением, доступом или активацией — напишите нам.\n"
        "Мы стараемся отвечать быстро и без лишней бюрократии.\n\n"
        f"{support_line}"
        "Можно открыть диалог прямо из бота или перейти в отдельный канал поддержки."
    )


def build_support_prompt_text() -> str:
    return (
        "💬 <b>Сообщение в поддержку</b>\n\n"
        "Опишите вопрос одним сообщением.\n"
        "Чем конкретнее формулировка, тем быстрее поможем."
    )


def _format_referral_line(item: ReferralInvitee) -> str:
    first_name = item.first_name
    username = item.username
    created_at = item.created_at
    name = first_name or (f"@{username}" if username else "Новый пользователь")
    return f"• <b>{escape(name)}</b> • {created_at.astimezone(UTC).strftime('%d.%m')}"


def _format_promo_line(promo: PromoCodeInfo) -> str:
    bonus = f" • +{promo.bonus_days} дней" if promo.bonus_days else ""
    return f"• <b>{escape(promo.title)}</b> — <code>{escape(promo.code)}</code>{bonus}"


def _format_review_line(review: PublicReview) -> str:
    first_name = review.first_name or "Пользователь Flow VPN"
    created_at = review.created_at.astimezone(UTC).strftime("%d.%m")
    return (
        f"⭐ <b>{escape(first_name)}</b> • {'★' * review.rating} • {created_at}\n"
        f"{escape(review.text)}"
    )
