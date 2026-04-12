# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.account import GetTelegramAccountUseCase
from src.application.runtime import GetAccessModeUseCase
from src.application.users import RegisterTelegramUserUseCase, TelegramUserData
from src.application.vpn import AcquireVpnAccessOutcome, AcquireVpnAccessUseCase
from src.presentation.telegram.callbacks import (
    ACTION_BUY,
    MENU_ACCOUNT,
    MENU_BUY,
    MENU_HOME,
)
from src.presentation.telegram.keyboards.start import (
    build_section_menu,
    build_start_menu,
    build_vpn_access_menu,
)
from src.presentation.telegram.screens.start import (
    build_account_screen,
    build_buy_screen,
    build_home_text,
    build_vpn_access_text,
)

router = Router(name="start")


def extract_referral_code(message_text: str | None) -> str | None:
    if not message_text:
        return None

    _, _, payload = message_text.partition(" ")
    if not payload.startswith("ref_"):
        return None

    referral_code = payload.removeprefix("ref_").strip().lower()
    return referral_code or None


async def safe_edit_message(
    callback: CallbackQuery,
    *,
    text: str,
    reply_markup: InlineKeyboardMarkup,
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc):
            raise


@router.message(CommandStart())
async def start_handler(
    message: Message,
    register_telegram_user: FromDishka[RegisterTelegramUserUseCase],
    settings: FromDishka[Settings],
) -> None:
    telegram_user = message.from_user
    if telegram_user is None:
        await message.answer(
            "👋 Добро пожаловать в Flow VPN.\n\n"
            "Не удалось определить ваш Telegram-профиль.\n"
            "Попробуйте отправить команду /start ещё раз."
        )
        return

    is_new_user = await register_telegram_user.execute(
        TelegramUserData(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            language_code=telegram_user.language_code,
            is_bot=telegram_user.is_bot,
            is_premium=telegram_user.is_premium,
        ),
        referral_code=extract_referral_code(message.text),
    )

    display_name = telegram_user.first_name or telegram_user.full_name or "друг"
    is_admin = settings.is_admin(telegram_user.id)
    await message.answer(
        build_home_text(display_name, is_new_user=is_new_user),
        reply_markup=build_start_menu(is_admin=is_admin),
    )


@router.callback_query(F.data == MENU_HOME)
async def home_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
) -> None:
    telegram_user = callback.from_user
    display_name = telegram_user.first_name or telegram_user.full_name or "друг"
    is_admin = settings.is_admin(telegram_user.id)

    await safe_edit_message(
        callback,
        text=build_home_text(display_name, is_new_user=False),
        reply_markup=build_start_menu(is_admin=is_admin),
    )
    await callback.answer()


@router.callback_query(F.data == MENU_BUY)
async def buy_section_callback_handler(
    callback: CallbackQuery,
    get_access_mode: FromDishka[GetAccessModeUseCase],
) -> None:
    access_mode = await get_access_mode.execute()
    screen = build_buy_screen(access_mode)

    await safe_edit_message(
        callback,
        text=screen.text,
        reply_markup=build_section_menu(
            action_text=screen.action_text,
            action_callback=screen.action_callback,
        ),
    )
    await callback.answer()


@router.callback_query(F.data == MENU_ACCOUNT)
async def account_section_callback_handler(
    callback: CallbackQuery,
    get_telegram_account: FromDishka[GetTelegramAccountUseCase],
) -> None:
    account = await get_telegram_account.execute(callback.from_user.id)
    if account is None:
        await callback.answer(
            "Профиль пока не найден. Отправьте /start ещё раз.",
            show_alert=True,
        )
        return

    screen = build_account_screen(account)
    await safe_edit_message(
        callback,
        text=screen.text,
        reply_markup=build_section_menu(
            action_text=screen.action_text,
            action_callback=screen.action_callback,
        ),
    )
    await callback.answer()
@router.callback_query(F.data == ACTION_BUY)
async def buy_action_callback_handler(
    callback: CallbackQuery,
    acquire_vpn_access: FromDishka[AcquireVpnAccessUseCase],
) -> None:
    result = await acquire_vpn_access.execute(callback.from_user.id)
    if result.outcome is AcquireVpnAccessOutcome.ACTIVE and result.access is not None:
        await safe_edit_message(
            callback,
            text=build_vpn_access_text(result.access),
            reply_markup=build_vpn_access_menu(
                subscription_url=result.access.subscription_url,
            ),
        )
        await callback.answer("Доступ готов")
        return

    await callback.answer(
        result.message or "Пока не удалось подготовить доступ.",
        show_alert=True,
    )
