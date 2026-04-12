# ruff: noqa: RUF001

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.app.config import Settings
from src.application.admin import (
    AdminUsersFilter,
    DisableAdminVpnAccessUseCase,
    GetAdminDashboardUseCase,
    GetAdminUserDetailUseCase,
    GetAdminUsersOverviewUseCase,
    IssueAdminVpnAccessUseCase,
    ReissueAdminVpnAccessUseCase,
    SearchAdminUsersUseCase,
)
from src.application.runtime import (
    AccessMode,
    GetAccessModeUseCase,
    SetAccessModeUseCase,
)
from src.presentation.telegram.callbacks import (
    ACTION_ADMIN_SET_FREE_ACCESS,
    ACTION_ADMIN_USERS_SEARCH,
    ADMIN_ACCESS_MODE_CALLBACKS,
    ADMIN_ACTION_CALLBACKS,
    ADMIN_SECTION_CALLBACKS,
    ADMIN_USER_DISABLE_PREFIX,
    ADMIN_USER_HISTORY_PREFIX,
    ADMIN_USER_ISSUE_PREFIX,
    ADMIN_USER_OPEN_ACCESS_PREFIX,
    ADMIN_USER_REISSUE_PREFIX,
    ADMIN_USER_VIEW_PREFIX,
    ADMIN_USERS_CALLBACKS,
    ADMIN_USERS_FILTER_PREFIX,
    ADMIN_USERS_PAGE_PREFIX,
    MENU_ADMIN_ACCESS,
    MENU_ADMIN_HOME,
    MENU_ADMIN_USERS,
)
from src.presentation.telegram.handlers.start import safe_edit_message
from src.presentation.telegram.keyboards.admin import (
    build_access_mode_menu,
    build_admin_menu,
    build_admin_section_menu,
    build_admin_user_access_menu,
    build_admin_user_detail_menu,
    build_admin_users_menu,
    build_admin_users_overview_menu,
)
from src.presentation.telegram.screens.admin import (
    ADMIN_ACTION_FEEDBACK,
    ADMIN_SECTION_SCREENS,
    build_access_mode_text,
    build_admin_home_text,
    build_admin_user_access_text,
    build_admin_user_detail_text,
    build_admin_user_history_text,
    build_admin_users_search_prompt_text,
    build_admin_users_search_result_text,
    build_admin_users_text,
)
from src.presentation.telegram.states import AdminUsersSearchState

router = Router(name="admin")


def is_admin_user(*, settings: Settings, telegram_user_id: int) -> bool:
    return settings.is_admin(telegram_user_id)


def parse_telegram_id_from_callback(data: str, prefix: str) -> int | None:
    if not data.startswith(prefix):
        return None

    raw_value = data.removeprefix(prefix)
    if not raw_value.isdigit():
        return None

    return int(raw_value)


def parse_admin_users_page(data: str) -> tuple[AdminUsersFilter, int] | None:
    if not data.startswith(ADMIN_USERS_PAGE_PREFIX):
        return None

    raw_value = data.removeprefix(ADMIN_USERS_PAGE_PREFIX)
    filter_value, separator, page_value = raw_value.partition(":")
    if not separator or not page_value.isdigit():
        return None

    try:
        current_filter = AdminUsersFilter(filter_value)
    except ValueError:
        return None

    return current_filter, int(page_value)


def parse_admin_users_filter(data: str) -> AdminUsersFilter | None:
    if not data.startswith(ADMIN_USERS_FILTER_PREFIX):
        return None

    raw_value = data.removeprefix(ADMIN_USERS_FILTER_PREFIX)
    try:
        return AdminUsersFilter(raw_value)
    except ValueError:
        return None


async def answer_access_denied(target: Message | CallbackQuery) -> None:
    if isinstance(target, Message):
        await target.answer("⛔ Доступ к этой панели ограничен.")
        return

    await target.answer("⛔ У вас нет доступа к этой панели.", show_alert=True)


@router.message(Command("admin"))
async def admin_entry_handler(
    message: Message,
    settings: FromDishka[Settings],
    get_admin_dashboard: FromDishka[GetAdminDashboardUseCase],
    state: FSMContext,
) -> None:
    telegram_user = message.from_user
    if telegram_user is None or not is_admin_user(
        settings=settings,
        telegram_user_id=telegram_user.id,
    ):
        await answer_access_denied(message)
        return

    display_name = telegram_user.first_name or telegram_user.full_name or "admin"
    dashboard = await get_admin_dashboard.execute()
    await state.clear()
    await message.answer(
        build_admin_home_text(display_name, dashboard),
        reply_markup=build_admin_menu(),
    )


@router.callback_query(F.data == MENU_ADMIN_HOME)
async def admin_home_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    get_admin_dashboard: FromDishka[GetAdminDashboardUseCase],
    state: FSMContext,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    display_name = telegram_user.first_name or telegram_user.full_name or "admin"
    dashboard = await get_admin_dashboard.execute()
    await state.clear()
    await safe_edit_message(
        callback,
        text=build_admin_home_text(display_name, dashboard),
        reply_markup=build_admin_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == MENU_ADMIN_ACCESS)
async def access_mode_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    get_access_mode: FromDishka[GetAccessModeUseCase],
    state: FSMContext,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    access_mode = await get_access_mode.execute()
    await state.clear()
    await safe_edit_message(
        callback,
        text=build_access_mode_text(access_mode),
        reply_markup=build_access_mode_menu(current_mode=access_mode),
    )
    await callback.answer()


@router.callback_query(F.data == MENU_ADMIN_USERS)
async def admin_users_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    get_admin_users_overview: FromDishka[GetAdminUsersOverviewUseCase],
    state: FSMContext,
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    overview = await get_admin_users_overview.execute()
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
    await callback.answer()


@router.callback_query(F.data.in_(ADMIN_USERS_CALLBACKS))
async def admin_users_action_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    get_admin_users_overview: FromDishka[GetAdminUsersOverviewUseCase],
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

    overview = await get_admin_users_overview.execute()
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
    await callback.answer("Список обновлён ✨")


@router.message(AdminUsersSearchState.waiting_query)
async def admin_users_search_message_handler(
    message: Message,
    settings: FromDishka[Settings],
    search_admin_users: FromDishka[SearchAdminUsersUseCase],
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

    result = await search_admin_users.execute(query)
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
    get_admin_users_overview: FromDishka[GetAdminUsersOverviewUseCase],
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
    overview = await get_admin_users_overview.execute(
        page=page,
        current_filter=current_filter,
    )
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
    await callback.answer()


@router.callback_query(F.data.startswith(ADMIN_USERS_FILTER_PREFIX))
async def admin_users_filter_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    get_admin_users_overview: FromDishka[GetAdminUsersOverviewUseCase],
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

    overview = await get_admin_users_overview.execute(current_filter=current_filter)
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
    await callback.answer("Фильтр обновлён ✨")


@router.callback_query(F.data.startswith(ADMIN_USER_VIEW_PREFIX))
async def admin_user_view_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    get_admin_user_detail: FromDishka[GetAdminUserDetailUseCase],
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

    target_telegram_id = parse_telegram_id_from_callback(callback_data, ADMIN_USER_VIEW_PREFIX)
    if target_telegram_id is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    detail = await get_admin_user_detail.execute(target_telegram_id)
    if detail is None:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return

    await state.clear()
    await safe_edit_message(
        callback,
        text=build_admin_user_detail_text(detail),
        reply_markup=build_admin_user_detail_menu(detail),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(ADMIN_USER_OPEN_ACCESS_PREFIX))
async def admin_user_open_access_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    get_admin_user_detail: FromDishka[GetAdminUserDetailUseCase],
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    callback_data = callback.data
    if callback_data is None:
        await callback.answer()
        return

    target_telegram_id = parse_telegram_id_from_callback(
        callback_data,
        ADMIN_USER_OPEN_ACCESS_PREFIX,
    )
    if target_telegram_id is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    detail = await get_admin_user_detail.execute(target_telegram_id)
    if detail is None or detail.vpn_access is None:
        await callback.answer("Активный доступ не найден.", show_alert=True)
        return

    await safe_edit_message(
        callback,
        text=build_admin_user_access_text(detail),
        reply_markup=build_admin_user_access_menu(
            subscription_url=detail.vpn_access.subscription_url,
            telegram_id=detail.user.telegram_id,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(ADMIN_USER_HISTORY_PREFIX))
async def admin_user_history_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    get_admin_user_detail: FromDishka[GetAdminUserDetailUseCase],
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    callback_data = callback.data
    if callback_data is None:
        await callback.answer()
        return

    target_telegram_id = parse_telegram_id_from_callback(callback_data, ADMIN_USER_HISTORY_PREFIX)
    if target_telegram_id is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    detail = await get_admin_user_detail.execute(target_telegram_id)
    if detail is None:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return

    await safe_edit_message(
        callback,
        text=build_admin_user_history_text(detail),
        reply_markup=build_admin_user_detail_menu(detail),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(ADMIN_USER_ISSUE_PREFIX))
async def admin_user_issue_access_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    issue_admin_vpn_access: FromDishka[IssueAdminVpnAccessUseCase],
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
        detail = await issue_admin_vpn_access.execute(
            target_telegram_id,
            actor_telegram_id=telegram_user.id,
        )
    except (RuntimeError, ValueError):
        await callback.answer("Не удалось выдать доступ прямо сейчас.", show_alert=True)
        return

    if detail is None:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return

    await safe_edit_message(
        callback,
        text=build_admin_user_detail_text(detail),
        reply_markup=build_admin_user_detail_menu(detail),
    )
    await callback.answer("Доступ выдан ✨")


@router.callback_query(F.data.startswith(ADMIN_USER_DISABLE_PREFIX))
async def admin_user_disable_access_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    disable_admin_vpn_access: FromDishka[DisableAdminVpnAccessUseCase],
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    callback_data = callback.data
    if callback_data is None:
        await callback.answer()
        return

    target_telegram_id = parse_telegram_id_from_callback(callback_data, ADMIN_USER_DISABLE_PREFIX)
    if target_telegram_id is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    try:
        detail = await disable_admin_vpn_access.execute(
            target_telegram_id,
            actor_telegram_id=telegram_user.id,
        )
    except (RuntimeError, ValueError):
        await callback.answer("Не удалось отключить доступ прямо сейчас.", show_alert=True)
        return

    if detail is None:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return
    if detail.vpn_access is None:
        await callback.answer("У пользователя нет активного доступа.", show_alert=True)
        return

    await safe_edit_message(
        callback,
        text=build_admin_user_detail_text(detail),
        reply_markup=build_admin_user_detail_menu(detail),
    )
    await callback.answer("Доступ отключён")


@router.callback_query(F.data.startswith(ADMIN_USER_REISSUE_PREFIX))
async def admin_user_reissue_access_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    reissue_admin_vpn_access: FromDishka[ReissueAdminVpnAccessUseCase],
) -> None:
    telegram_user = callback.from_user
    if not is_admin_user(settings=settings, telegram_user_id=telegram_user.id):
        await answer_access_denied(callback)
        return

    callback_data = callback.data
    if callback_data is None:
        await callback.answer()
        return

    target_telegram_id = parse_telegram_id_from_callback(callback_data, ADMIN_USER_REISSUE_PREFIX)
    if target_telegram_id is None:
        await callback.answer("Не удалось определить пользователя.", show_alert=True)
        return

    try:
        detail = await reissue_admin_vpn_access.execute(
            target_telegram_id,
            actor_telegram_id=telegram_user.id,
        )
    except (RuntimeError, ValueError):
        await callback.answer("Не удалось перевыпустить доступ.", show_alert=True)
        return

    if detail is None:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return
    if detail.vpn_access is None:
        await callback.answer("У пользователя пока нет доступа.", show_alert=True)
        return

    await safe_edit_message(
        callback,
        text=build_admin_user_detail_text(detail),
        reply_markup=build_admin_user_detail_menu(detail),
    )
    await callback.answer("Доступ перевыпущен ✨")


@router.callback_query(
    F.data.in_(
        ADMIN_SECTION_CALLBACKS - {MENU_ADMIN_HOME, MENU_ADMIN_ACCESS, MENU_ADMIN_USERS}
    )
)
async def admin_section_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
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

    screen = ADMIN_SECTION_SCREENS[callback_data]
    await state.clear()
    await safe_edit_message(
        callback,
        text=screen.text,
        reply_markup=build_admin_section_menu(
            action_text=screen.action_text,
            action_callback=screen.action_callback,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.in_(ADMIN_ACCESS_MODE_CALLBACKS))
async def admin_access_mode_action_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
    get_access_mode: FromDishka[GetAccessModeUseCase],
    set_access_mode: FromDishka[SetAccessModeUseCase],
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

    target_mode = (
        AccessMode.FREE_ACCESS
        if callback_data == ACTION_ADMIN_SET_FREE_ACCESS
        else AccessMode.BILLING_ENABLED
    )
    current_mode = await get_access_mode.execute()
    if current_mode is not target_mode:
        current_mode = await set_access_mode.execute(target_mode)

    await state.clear()
    await safe_edit_message(
        callback,
        text=build_access_mode_text(current_mode),
        reply_markup=build_access_mode_menu(current_mode=current_mode),
    )
    await callback.answer("Режим обновлён ✨")


@router.callback_query(F.data.in_(ADMIN_ACTION_CALLBACKS))
async def admin_action_callback_handler(
    callback: CallbackQuery,
    settings: FromDishka[Settings],
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

    await state.clear()
    await callback.answer(ADMIN_ACTION_FEEDBACK[callback_data], show_alert=True)
