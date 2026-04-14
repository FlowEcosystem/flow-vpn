# ruff: noqa: RUF001

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.application.admin import AdminService, AdminUsersFilter
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import (
    build_admin_user_detail_menu,
    build_admin_users_overview_menu,
)
from src.presentation.telegram.screens.admin import (
    build_admin_user_detail_text,
    build_admin_users_text,
)


async def render_users_overview(
    callback: CallbackQuery,
    *,
    admin: AdminService,
    state: FSMContext,
    page: int = 0,
    current_filter: AdminUsersFilter = AdminUsersFilter.ALL,
) -> None:
    overview = await admin.get_users_overview(page=page, current_filter=current_filter)
    await state.clear()
    await safe_edit_message(
        callback,
        text=build_admin_users_text(overview),
        reply_markup=build_admin_users_overview_menu(
            users=overview.recent_users,
            current_page=overview.current_page,
            has_next_page=overview.has_next_page,
            current_filter=overview.current_filter,
        ),
    )


async def render_user_detail(callback: CallbackQuery, detail) -> None:
    await safe_edit_message(
        callback,
        text=build_admin_user_detail_text(detail),
        reply_markup=build_admin_user_detail_menu(detail),
    )
