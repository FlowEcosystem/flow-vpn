# ruff: noqa: RUF001

from src.application.promos import AdminPromoDetail
from src.presentation.telegram.datetime import format_datetime_msk


def build_admin_promos_list_text(promos: tuple[AdminPromoDetail, ...]) -> str:
    if not promos:
        promos_block = "Промокодов пока нет."
    else:
        promos_block = "\n".join(_format_admin_promo_line(p) for p in promos)

    return (
        "🎁 <b>Промокоды</b>\n\n"
        f"Всего: <b>{len(promos)}</b> · "
        f"Активных: <b>{sum(1 for p in promos if p.is_active)}</b>\n\n"
        f"{promos_block}"
    )


def build_admin_promo_detail_text(promo: AdminPromoDetail) -> str:
    status = "✅ активен" if promo.is_active else "⛔ деактивирован"
    if promo.is_infinite:
        bonus = "♾️ бессрочная подписка"
    elif promo.bonus_days:
        bonus = f"+{promo.bonus_days} дн."
    else:
        bonus = "нет"
    scope = "все подписки" if promo.apply_to_all else "первая активная"
    limit = str(promo.max_redemptions) if promo.max_redemptions else "без лимита"
    expires = format_datetime_msk(promo.expires_at) if promo.expires_at else "не задан"
    created = format_datetime_msk(promo.created_at)
    return (
        f"🏷 <b>{promo.code}</b>\n\n"
        f"• Название: <b>{promo.title}</b>\n"
        f"• Статус: <b>{status}</b>\n"
        f"• Бонус: <b>{bonus}</b>\n"
        f"• Применяется к: <b>{scope}</b>\n"
        f"• Активаций: <b>{promo.current_redemptions}</b> / <b>{limit}</b>\n"
        f"• Истекает: <b>{expires}</b>\n"
        f"• Создан: <b>{created}</b>"
    )


def _format_admin_promo_line(promo: AdminPromoDetail) -> str:
    status = "✅" if promo.is_active else "⛔"
    if promo.is_infinite:
        bonus = " · ♾️"
    elif promo.bonus_days:
        bonus = f" · +{promo.bonus_days}д."
    else:
        bonus = ""
    scope = "" if promo.apply_to_all else " · 1 подп."
    return (
        f"{status} <code>{promo.code}</code> — {promo.title}{bonus}{scope}"
        f" · {promo.current_redemptions} акт."
    )
