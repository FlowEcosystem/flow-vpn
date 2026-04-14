# ruff: noqa: RUF001

from uuid import UUID

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.application.account import AccountService
from src.application.vpn import VpnService
from src.presentation.telegram.callbacks import (
    MENU_ACCOUNT,
    MENU_BUY,
    USER_ACCESS_DELETE_PREFIX,
    USER_ACCESS_DISABLE_PREFIX,
    USER_ACCESS_ENABLE_PREFIX,
    USER_ACCESS_VIEW_PREFIX,
)
from src.presentation.telegram.keyboards.start import (
    build_section_menu,
    build_subscription_detail_menu,
    build_subscriptions_list_menu,
)
from src.presentation.telegram.screens.start import (
    build_account_screen,
    build_subscription_detail_text,
    build_subscriptions_list_text,
)

from .common import safe_edit_message

router = Router(name="start_account")


@router.callback_query(F.data == MENU_ACCOUNT)
async def account_section_callback_handler(
    callback: CallbackQuery,
    account_service: FromDishka[AccountService],
) -> None:
    account = await account_service.get_account(callback.from_user.id)
    if account is None:
        await callback.answer(
            "Профиль пока не найден. Отправьте /start ещё раз.",
            show_alert=True,
        )
        return

    if account.vpn_accesses:
        await safe_edit_message(
            callback,
            text=build_subscriptions_list_text(account.vpn_accesses),
            reply_markup=build_subscriptions_list_menu(account.vpn_accesses),
        )
    else:
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


@router.callback_query(F.data.startswith(USER_ACCESS_VIEW_PREFIX))
async def user_access_view_callback_handler(
    callback: CallbackQuery,
    account_service: FromDishka[AccountService],
) -> None:
    raw_id = (callback.data or "").removeprefix(USER_ACCESS_VIEW_PREFIX)
    account = await account_service.get_account(callback.from_user.id)
    if account is None:
        await callback.answer("Профиль не найден.", show_alert=True)
        return

    target = next((a for a in account.vpn_accesses if str(a.id) == raw_id), None)
    if target is None:
        await callback.answer("Подписка не найдена.", show_alert=True)
        return

    index = next(i for i, a in enumerate(account.vpn_accesses, 1) if a.id == target.id)
    await safe_edit_message(
        callback,
        text=build_subscription_detail_text(target, index),
        reply_markup=build_subscription_detail_menu(target),
    )
    await callback.answer()


async def _handle_user_access_mutation_error(
    callback: CallbackQuery,
    *,
    title: str,
) -> None:
    message = callback.message
    if isinstance(message, Message):
        await message.edit_text(
            f"⚠️ <b>{title}</b>\n\n"
            "Попробуйте позже или обратитесь в поддержку.",
            reply_markup=build_section_menu(
                action_text="📋 Мои подписки",
                action_callback=MENU_ACCOUNT,
            ),
        )


async def _render_account_after_access_change(
    callback: CallbackQuery,
    *,
    account_service: AccountService,
) -> None:
    account = await account_service.get_account(callback.from_user.id)
    if account is None:
        return

    await safe_edit_message(
        callback,
        text=build_subscriptions_list_text(account.vpn_accesses),
        reply_markup=build_subscriptions_list_menu(account.vpn_accesses),
    )


@router.callback_query(F.data.startswith(USER_ACCESS_ENABLE_PREFIX))
async def user_access_enable_callback_handler(
    callback: CallbackQuery,
    vpn: FromDishka[VpnService],
    account_service: FromDishka[AccountService],
) -> None:
    raw_id = (callback.data or "").removeprefix(USER_ACCESS_ENABLE_PREFIX)
    try:
        access_id = UUID(raw_id)
    except ValueError:
        await callback.answer("Некорректный идентификатор подписки.", show_alert=True)
        return

    await callback.answer("⏳ Возобновляем подписку...")
    try:
        await vpn.enable(callback.from_user.id, access_id)
    except (RuntimeError, ValueError):
        await _handle_user_access_mutation_error(
            callback,
            title="Не удалось возобновить подписку",
        )
        return

    await _render_account_after_access_change(
        callback,
        account_service=account_service,
    )


@router.callback_query(F.data.startswith(USER_ACCESS_DISABLE_PREFIX))
async def user_access_disable_callback_handler(
    callback: CallbackQuery,
    vpn: FromDishka[VpnService],
    account_service: FromDishka[AccountService],
) -> None:
    raw_id = (callback.data or "").removeprefix(USER_ACCESS_DISABLE_PREFIX)
    try:
        access_id = UUID(raw_id)
    except ValueError:
        await callback.answer("Некорректный идентификатор подписки.", show_alert=True)
        return

    await callback.answer("⏳ Отключаем подписку...")
    try:
        await vpn.disable(callback.from_user.id, access_id)
    except (RuntimeError, ValueError):
        await _handle_user_access_mutation_error(
            callback,
            title="Не удалось отключить подписку",
        )
        return

    await _render_account_after_access_change(
        callback,
        account_service=account_service,
    )


@router.callback_query(F.data.startswith(USER_ACCESS_DELETE_PREFIX))
async def user_access_delete_callback_handler(
    callback: CallbackQuery,
    vpn: FromDishka[VpnService],
    account_service: FromDishka[AccountService],
) -> None:
    raw_id = (callback.data or "").removeprefix(USER_ACCESS_DELETE_PREFIX)
    try:
        access_id = UUID(raw_id)
    except ValueError:
        await callback.answer("Некорректный идентификатор подписки.", show_alert=True)
        return

    await callback.answer("⏳ Удаляем подписку...")
    try:
        is_deleted = await vpn.delete(callback.from_user.id, access_id)
    except (RuntimeError, ValueError):
        await _handle_user_access_mutation_error(
            callback,
            title="Не удалось удалить подписку",
        )
        return

    if not is_deleted:
        await callback.answer("Подписка не найдена.", show_alert=True)
        return

    account = await account_service.get_account(callback.from_user.id)
    if account is None:
        return

    if account.vpn_accesses:
        await safe_edit_message(
            callback,
            text=build_subscriptions_list_text(account.vpn_accesses),
            reply_markup=build_subscriptions_list_menu(account.vpn_accesses),
        )
        return

    await safe_edit_message(
        callback,
        text=(
            "📋 <b>Мои подписки</b>\n\n"
            "У вас пока нет подписок.\n\n"
            "Нажмите «Получить VPN», чтобы оформить новую."
        ),
        reply_markup=build_section_menu(
            action_text="⚡ Получить VPN",
            action_callback=MENU_BUY,
        ),
    )
