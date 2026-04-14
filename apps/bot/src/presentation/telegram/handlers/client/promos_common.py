from src.application.promos import PromoService
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.client import (
    build_promo_menu,
    build_promo_select_access_menu,
)
from src.presentation.telegram.screens.client import (
    build_promo_result_text,
    build_promo_select_access_text,
)

from aiogram.types import CallbackQuery, Message


async def handle_promo_apply_by_code(
    *,
    callback: CallbackQuery,
    code: str,
    promos: PromoService,
) -> None:
    eligibility = await promos.check_eligibility(callback.from_user.id, code=code)

    if eligibility.promo is None:
        await callback.answer("Промокод не найден или уже недоступен.", show_alert=True)
        return

    if eligibility.already_used:
        await callback.answer("Этот промокод уже активирован в твоём аккаунте.", show_alert=True)
        return

    has_effect = eligibility.promo.bonus_days > 0 or eligibility.promo.is_infinite
    if has_effect and not eligibility.eligible_accesses:
        await callback.answer(
            "Нет подходящих подписок. Промокод действует только на активные подписки с конечным сроком.",
            show_alert=True,
        )
        return

    if has_effect and not eligibility.promo.apply_to_all and len(eligibility.eligible_accesses) > 1:
        await safe_edit_message(
            callback,
            text=build_promo_select_access_text(eligibility.promo, eligibility.eligible_accesses),
            reply_markup=build_promo_select_access_menu(code.upper(), eligibility.eligible_accesses),
        )
        await callback.answer()
        return

    target_id = (
        eligibility.eligible_accesses[0].access_id
        if has_effect and not eligibility.promo.apply_to_all
        else None
    )
    result = await promos.apply(callback.from_user.id, code=code, target_access_id=target_id)
    overview = await promos.get_overview(callback.from_user.id)
    await safe_edit_message(
        callback,
        text=build_promo_result_text(result),
        reply_markup=build_promo_menu(overview),
    )
    await callback.answer()


async def handle_promo_apply_by_code_message(
    *,
    message: Message,
    code: str,
    promos: PromoService,
) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        return

    eligibility = await promos.check_eligibility(telegram_user.id, code=code)

    if eligibility.promo is None:
        overview = await promos.get_overview(telegram_user.id)
        await message.answer(
            "❌ Промокод не найден или уже недоступен.",
            reply_markup=build_promo_menu(overview),
        )
        return

    if eligibility.already_used:
        overview = await promos.get_overview(telegram_user.id)
        await message.answer(
            "❌ Этот промокод уже активирован в твоём аккаунте.",
            reply_markup=build_promo_menu(overview),
        )
        return

    has_effect = eligibility.promo.bonus_days > 0 or eligibility.promo.is_infinite
    if has_effect and not eligibility.eligible_accesses:
        overview = await promos.get_overview(telegram_user.id)
        await message.answer(
            "⚠️ Нет подходящих подписок. Промокод действует только на активные подписки с конечным сроком.",
            reply_markup=build_promo_menu(overview),
        )
        return

    if has_effect and not eligibility.promo.apply_to_all and len(eligibility.eligible_accesses) > 1:
        await message.answer(
            text=build_promo_select_access_text(eligibility.promo, eligibility.eligible_accesses),
            reply_markup=build_promo_select_access_menu(
                code.strip().upper(), eligibility.eligible_accesses
            ),
        )
        return

    target_id = (
        eligibility.eligible_accesses[0].access_id
        if has_effect and not eligibility.promo.apply_to_all
        else None
    )
    result = await promos.apply(telegram_user.id, code=code, target_access_id=target_id)
    overview = await promos.get_overview(telegram_user.id)
    await message.answer(
        build_promo_result_text(result),
        reply_markup=build_promo_menu(overview),
    )
