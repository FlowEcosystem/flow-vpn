# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.application.runtime import RuntimeSettingsService
from src.application.vpn import AcquireVpnAccessOutcome, VpnService
from src.presentation.telegram.callbacks import ACTION_BUY, MENU_BUY
from src.presentation.telegram.keyboards.start import build_section_menu, build_vpn_access_menu
from src.presentation.telegram.screens.start import build_buy_screen, build_vpn_access_text

from .common import safe_edit_message

router = Router(name="start_buy")


@router.callback_query(F.data == MENU_BUY)
async def buy_section_callback_handler(
    callback: CallbackQuery,
    runtime_settings: FromDishka[RuntimeSettingsService],
) -> None:
    access_mode = await runtime_settings.get_access_mode()
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


@router.callback_query(F.data == ACTION_BUY)
async def buy_action_callback_handler(
    callback: CallbackQuery,
    vpn: FromDishka[VpnService],
) -> None:
    await callback.answer("⏳ Готовим подключение...")
    result = await vpn.acquire(callback.from_user.id)
    if result.outcome is AcquireVpnAccessOutcome.ACTIVE and result.access is not None:
        await safe_edit_message(
            callback,
            text=build_vpn_access_text(result.access),
            reply_markup=build_vpn_access_menu(
                subscription_url=result.access.subscription_url,
            ),
        )
        return

    message = callback.message
    if isinstance(message, Message):
        error_text = result.message or "Пока не удалось подготовить доступ."
        await message.edit_text(
            f"⚠️ <b>Не удалось подключить</b>\n\n{error_text}",
            reply_markup=build_section_menu(
                action_text="🔄 Попробовать снова",
                action_callback=ACTION_BUY,
            ),
        )
