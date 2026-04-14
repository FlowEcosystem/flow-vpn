# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.admin import AdminService
from src.presentation.telegram.callbacks import (
    ADMIN_USERS_BULK_DELETE_PREFIX,
    ADMIN_USERS_BULK_DISABLE_PREFIX,
    ADMIN_USERS_BULK_ISSUE_PREFIX,
    ADMIN_USERS_BULK_MENU_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_DELETE_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_DISABLE_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_ISSUE_PREFIX,
    ADMIN_USERS_GLOBAL_BULK_MENU_PREFIX,
)
from src.presentation.telegram.keyboards.admin import (
    build_admin_users_bulk_actions_menu,
    build_admin_users_bulk_delete_confirm_menu,
    build_admin_users_bulk_disable_confirm_menu,
    build_admin_users_bulk_issue_confirm_menu,
    build_admin_users_global_bulk_actions_menu,
    build_admin_users_global_bulk_delete_confirm_menu,
    build_admin_users_global_bulk_disable_confirm_menu,
    build_admin_users_global_bulk_issue_confirm_menu,
)
from src.presentation.telegram.screens.admin import (
    build_admin_users_bulk_actions_text,
    build_admin_users_bulk_delete_confirm_text,
    build_admin_users_bulk_disable_confirm_text,
    build_admin_users_bulk_issue_confirm_text,
    build_admin_users_global_bulk_actions_text,
    build_admin_users_global_bulk_delete_confirm_text,
    build_admin_users_global_bulk_disable_confirm_text,
    build_admin_users_global_bulk_issue_confirm_text,
)

from .users_bulk_common import show_bulk_screen

router = Router(name="admin_users_bulk_menu")


@router.callback_query(F.data.startswith(ADMIN_USERS_BULK_ISSUE_PREFIX))
async def admin_users_bulk_issue_prepare_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    await show_bulk_screen(
        callback=callback,
        settings=settings,
        admin=admin,
        state=state,
        action_prefix=ADMIN_USERS_BULK_ISSUE_PREFIX,
        parse_error_message="Не удалось определить страницу.",
        empty_message="На этой странице нет пользователей.",
        is_empty=lambda overview: not overview.recent_users,
        render_text=build_admin_users_bulk_issue_confirm_text,
        render_menu=build_admin_users_bulk_issue_confirm_menu,
    )


@router.callback_query(F.data.startswith(ADMIN_USERS_GLOBAL_BULK_ISSUE_PREFIX))
async def admin_users_global_bulk_issue_prepare_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    await show_bulk_screen(
        callback=callback,
        settings=settings,
        admin=admin,
        state=state,
        action_prefix=ADMIN_USERS_GLOBAL_BULK_ISSUE_PREFIX,
        parse_error_message="Не удалось определить сегмент.",
        empty_message="В этом сегменте нет пользователей.",
        is_empty=lambda overview: overview.total_filtered == 0,
        render_text=build_admin_users_global_bulk_issue_confirm_text,
        render_menu=build_admin_users_global_bulk_issue_confirm_menu,
    )


@router.callback_query(F.data.startswith(ADMIN_USERS_BULK_MENU_PREFIX))
async def admin_users_bulk_menu_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    await show_bulk_screen(
        callback=callback,
        settings=settings,
        admin=admin,
        state=state,
        action_prefix=ADMIN_USERS_BULK_MENU_PREFIX,
        parse_error_message="Не удалось определить страницу.",
        empty_message="На этой странице нет пользователей.",
        is_empty=lambda overview: not overview.recent_users,
        render_text=build_admin_users_bulk_actions_text,
        render_menu=build_admin_users_bulk_actions_menu,
    )


@router.callback_query(F.data.startswith(ADMIN_USERS_GLOBAL_BULK_MENU_PREFIX))
async def admin_users_global_bulk_menu_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    await show_bulk_screen(
        callback=callback,
        settings=settings,
        admin=admin,
        state=state,
        action_prefix=ADMIN_USERS_GLOBAL_BULK_MENU_PREFIX,
        parse_error_message="Не удалось определить страницу.",
        empty_message="В этом сегменте нет пользователей.",
        is_empty=lambda overview: overview.total_filtered == 0,
        render_text=build_admin_users_global_bulk_actions_text,
        render_menu=build_admin_users_global_bulk_actions_menu,
    )


@router.callback_query(F.data.startswith(ADMIN_USERS_BULK_DISABLE_PREFIX))
async def admin_users_bulk_disable_prepare_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    await show_bulk_screen(
        callback=callback,
        settings=settings,
        admin=admin,
        state=state,
        action_prefix=ADMIN_USERS_BULK_DISABLE_PREFIX,
        parse_error_message="Не удалось определить страницу.",
        empty_message="На этой странице нет пользователей.",
        is_empty=lambda overview: not overview.recent_users,
        render_text=build_admin_users_bulk_disable_confirm_text,
        render_menu=build_admin_users_bulk_disable_confirm_menu,
    )


@router.callback_query(F.data.startswith(ADMIN_USERS_GLOBAL_BULK_DISABLE_PREFIX))
async def admin_users_global_bulk_disable_prepare_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    await show_bulk_screen(
        callback=callback,
        settings=settings,
        admin=admin,
        state=state,
        action_prefix=ADMIN_USERS_GLOBAL_BULK_DISABLE_PREFIX,
        parse_error_message="Не удалось определить сегмент.",
        empty_message="В этом сегменте нет пользователей.",
        is_empty=lambda overview: overview.total_filtered == 0,
        render_text=build_admin_users_global_bulk_disable_confirm_text,
        render_menu=build_admin_users_global_bulk_disable_confirm_menu,
    )


@router.callback_query(F.data.startswith(ADMIN_USERS_BULK_DELETE_PREFIX))
async def admin_users_bulk_delete_prepare_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    await show_bulk_screen(
        callback=callback,
        settings=settings,
        admin=admin,
        state=state,
        action_prefix=ADMIN_USERS_BULK_DELETE_PREFIX,
        parse_error_message="Не удалось определить страницу.",
        empty_message="На этой странице нет пользователей.",
        is_empty=lambda overview: not overview.recent_users,
        render_text=build_admin_users_bulk_delete_confirm_text,
        render_menu=build_admin_users_bulk_delete_confirm_menu,
    )


@router.callback_query(F.data.startswith(ADMIN_USERS_GLOBAL_BULK_DELETE_PREFIX))
async def admin_users_global_bulk_delete_prepare_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    await show_bulk_screen(
        callback=callback,
        settings=settings,
        admin=admin,
        state=state,
        action_prefix=ADMIN_USERS_GLOBAL_BULK_DELETE_PREFIX,
        parse_error_message="Не удалось определить сегмент.",
        empty_message="В этом сегменте нет пользователей.",
        is_empty=lambda overview: overview.total_filtered == 0,
        render_text=build_admin_users_global_bulk_delete_confirm_text,
        render_menu=build_admin_users_global_bulk_delete_confirm_menu,
    )
