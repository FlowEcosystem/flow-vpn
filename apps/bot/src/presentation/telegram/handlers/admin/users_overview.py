# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.admin import AdminService, AdminUsersFilter
from src.presentation.telegram.callbacks import (
    ACTION_ADMIN_USERS_SEARCH,
    ADMIN_USERS_CALLBACKS,
    ADMIN_USERS_FILTER_PREFIX,
    ADMIN_USERS_PAGE_PREFIX,
    MENU_ADMIN_USERS,
)
from src.presentation.telegram.keyboards.admin import build_admin_users_menu, build_admin_users_overview_menu
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.screens.admin import (
    build_admin_users_search_prompt_text,
    build_admin_users_search_result_text,
)
from src.presentation.telegram.states import AdminUsersSearchState

from .common import (
    answer_access_denied,
    is_admin_user,
    parse_admin_users_filter,
    parse_admin_users_page,
)
from .users_common import render_users_overview

router = Router(name="admin_users_overview")


@router.callback_query(F.data == MENU_ADMIN_USERS)
async def admin_users_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    await render_users_overview(callback, admin=admin, state=state)
    await callback.answer()


@router.callback_query(F.data.in_(ADMIN_USERS_CALLBACKS))
async def admin_users_action_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    callback_data = callback.data
    if callback_data is None:
        await callback.answer()
        return

    if callback_data == ACTION_ADMIN_USERS_SEARCH:
        await state.set_state(AdminUsersSearchState.waiting_query)
        await safe_edit_message(
            callback,
            text=build_admin_users_search_prompt_text(),
            reply_markup=build_admin_users_menu(),
        )
        await callback.answer("Ожидаю запрос 🔎")
        return

    await render_users_overview(callback, admin=admin, state=state)
    await callback.answer("Список обновлён ✨")


@router.message(AdminUsersSearchState.waiting_query)
async def admin_users_search_message_handler(
    message: Message,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    telegram_user = message.from_user
    if telegram_user is None or not is_admin_user(
        settings=settings,
        telegram_user_id=telegram_user.id,
    ):
        await state.clear()
        await answer_access_denied(message)
        return

    query = (message.text or "").strip()
    if not query:
        await message.answer("Введите Telegram ID, @username или имя пользователя.")
        return

    result = await admin.search_users(query)
    await state.clear()
    await message.answer(
        build_admin_users_search_result_text(result),
        reply_markup=build_admin_users_overview_menu(
            users=result.users,
            current_page=0,
            has_next_page=False,
            current_filter=AdminUsersFilter.ALL,
        ),
    )


@router.callback_query(F.data.startswith(ADMIN_USERS_PAGE_PREFIX))
async def admin_users_page_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    callback_data = callback.data
    if callback_data is None:
        await callback.answer()
        return

    parsed = parse_admin_users_page(callback_data)
    if parsed is None:
        await callback.answer("Не удалось открыть страницу.", show_alert=True)
        return

    current_filter, page = parsed
    await render_users_overview(
        callback,
        admin=admin,
        state=state,
        page=page,
        current_filter=current_filter,
    )
    await callback.answer()


@router.callback_query(F.data.startswith(ADMIN_USERS_FILTER_PREFIX))
async def admin_users_filter_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    admin: FromDishka[AdminService],
    state: FSMContext,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    callback_data = callback.data
    if callback_data is None:
        await callback.answer()
        return

    current_filter = parse_admin_users_filter(callback_data)
    if current_filter is None:
        await callback.answer("Не удалось применить фильтр.", show_alert=True)
        return

    await render_users_overview(
        callback,
        admin=admin,
        state=state,
        current_filter=current_filter,
    )
    await callback.answer("Фильтр обновлён ✨")
