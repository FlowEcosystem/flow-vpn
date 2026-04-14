# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.admin import AdminService
from src.presentation.telegram.callbacks import (
    ADMIN_ACCESS_DELETE_PREFIX,
    ADMIN_ACCESS_DISABLE_PREFIX,
    ADMIN_ACCESS_ENABLE_PREFIX,
    ADMIN_ACCESS_REISSUE_PREFIX,
    ADMIN_USER_ISSUE_PREFIX,
)

from .common import answer_access_denied, is_admin_user, parse_telegram_id_from_callback, parse_uuid_from_callback
from .users_common import render_user_detail

router = Router(name="admin_users_access_actions")


async def _handle_user_issue_action(
    callback: CallbackQuery,
    *,
    settings: Settings,
    admin: AdminService,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    callback_data = callback.data
    if callback_data is None:
        await callback.answer()
        return

    target_telegram_id = parse_telegram_id_from_callback(callback_data, ADMIN_USER_ISSUE_PREFIX)
    if target_telegram_id is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    try:
        detail = await admin.issue_access(
            target_telegram_id,
            actor_telegram_id=telegram_user.id,
        )
    except (RuntimeError, ValueError):
        await callback.answer("Не удалось выдать доступ прямо сейчас.", show_alert=True)
        return

    if detail is None:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return

    await render_user_detail(callback, detail)
    await callback.answer("Доступ выдан ✨")


async def _handle_access_action(
    callback: CallbackQuery,
    *,
    settings: Settings,
    action_prefix: str,
    parse_error: str,
    missing_error: str,
    runtime_error: str,
    success_message: str,
    operation,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    callback_data = callback.data
    if callback_data is None:
        await callback.answer()
        return

    access_id = parse_uuid_from_callback(callback_data, action_prefix)
    if access_id is None:
        await callback.answer(parse_error, show_alert=True)
        return

    try:
        detail = await operation(access_id, telegram_user.id)
    except (RuntimeError, ValueError):
        await callback.answer(runtime_error, show_alert=True)
        return

    if detail is None:
        await callback.answer(missing_error, show_alert=True)
        return

    await render_user_detail(callback, detail)
    await callback.answer(success_message)


@router.callback_query(F.data.startswith(ADMIN_USER_ISSUE_PREFIX))
async def admin_user_issue_access_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
) -> None:
    await _handle_user_issue_action(callback, settings=settings, admin=admin)


@router.callback_query(F.data.startswith(ADMIN_ACCESS_ENABLE_PREFIX))
async def admin_access_enable_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
) -> None:
    await _handle_access_action(
        callback,
        settings=settings,
        action_prefix=ADMIN_ACCESS_ENABLE_PREFIX,
        parse_error="Не удалось определить подписку.",
        missing_error="Подписка не найдена.",
        runtime_error="Не удалось включить подписку прямо сейчас.",
        success_message="Подписка включена ✨",
        operation=lambda access_id, actor_id: admin.enable_access(access_id, actor_telegram_id=actor_id),
    )


@router.callback_query(F.data.startswith(ADMIN_ACCESS_DISABLE_PREFIX))
async def admin_access_disable_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
) -> None:
    await _handle_access_action(
        callback,
        settings=settings,
        action_prefix=ADMIN_ACCESS_DISABLE_PREFIX,
        parse_error="Не удалось определить подписку.",
        missing_error="Подписка не найдена.",
        runtime_error="Не удалось отключить подписку.",
        success_message="Подписка отключена",
        operation=lambda access_id, actor_id: admin.disable_access(access_id, actor_telegram_id=actor_id),
    )


@router.callback_query(F.data.startswith(ADMIN_ACCESS_REISSUE_PREFIX))
async def admin_access_reissue_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
) -> None:
    await _handle_access_action(
        callback,
        settings=settings,
        action_prefix=ADMIN_ACCESS_REISSUE_PREFIX,
        parse_error="Не удалось определить подписку.",
        missing_error="Подписка не найдена.",
        runtime_error="Не удалось перевыпустить подписку.",
        success_message="Подписка перевыпущена ✨",
        operation=lambda access_id, actor_id: admin.reissue_access(access_id, actor_telegram_id=actor_id),
    )


@router.callback_query(F.data.startswith(ADMIN_ACCESS_DELETE_PREFIX))
async def admin_access_delete_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
) -> None:
    await _handle_access_action(
        callback,
        settings=settings,
        action_prefix=ADMIN_ACCESS_DELETE_PREFIX,
        parse_error="Не удалось определить подписку.",
        missing_error="Подписка не найдена.",
        runtime_error="Не удалось удалить подписку.",
        success_message="Подписка удалена",
        operation=lambda access_id, actor_id: admin.delete_access(access_id, actor_telegram_id=actor_id),
    )
