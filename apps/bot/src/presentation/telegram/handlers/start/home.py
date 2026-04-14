# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.users import TelegramUserData, UsersService
from src.presentation.telegram.callbacks import MENU_HOME
from src.presentation.telegram.keyboards.start import build_start_menu
from src.presentation.telegram.screens.start import build_home_text

from .common import extract_referral_code, safe_edit_message

router = Router(name="start_home")


@router.message(CommandStart())
async def start_handler(
    message: Message,
    users: FromDishka[UsersService],
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

    is_new_user = await users.register(
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
