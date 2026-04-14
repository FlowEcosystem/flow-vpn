# ruff: noqa: RUF001

from urllib.parse import quote

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.referrals import ReferralsService
from src.presentation.telegram.callbacks import ACTION_REFER, MENU_REFER
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.client import build_referral_menu
from src.presentation.telegram.screens.client import build_referral_text

router = Router(name="client_referrals")


async def resolve_bot_username(bot: Bot, settings: Settings) -> str | None:
    if settings.bot_public_username:
        return settings.bot_public_username.removeprefix("@")
    me = await bot.get_me()
    return me.username


def build_referral_link(*, bot_username: str | None, referral_code: str) -> str | None:
    if not bot_username:
        return None

    deep_link = f"https://t.me/{bot_username}?start=ref_{referral_code}"
    share_text = "Подключайся к Flow VPN по моей ссылке:"
    encoded_url = quote(deep_link, safe="")
    encoded_text = quote(share_text, safe="")
    return f"https://t.me/share/url?url={encoded_url}&text={encoded_text}"


@router.callback_query(F.data == MENU_REFER)
@router.callback_query(F.data == ACTION_REFER)
async def referral_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    referrals: FromDishka[ReferralsService],
    state: FSMContext,
) -> None:
    overview = await referrals.get_overview(callback.from_user.id)
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
    await callback.answer()
