# ruff: noqa: RUF001

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.admin import AdminUsersFilter
from src.application.admin.dto import AdminUserDetail
from src.application.runtime import AccessMode
from src.application.users import UserSummary
from src.presentation.telegram.callbacks import (
    ACTION_ADMIN_SET_BILLING_ENABLED,
    ACTION_ADMIN_SET_FREE_ACCESS,
    ACTION_ADMIN_USERS_REFRESH,
    ACTION_ADMIN_USERS_SEARCH,
    ADMIN_USER_DISABLE_PREFIX,
    ADMIN_USER_HISTORY_PREFIX,
    ADMIN_USER_ISSUE_PREFIX,
    ADMIN_USER_OPEN_ACCESS_PREFIX,
    ADMIN_USER_REISSUE_PREFIX,
    ADMIN_USER_VIEW_PREFIX,
    ADMIN_USERS_FILTER_PREFIX,
    ADMIN_USERS_PAGE_PREFIX,
    MENU_ADMIN_ACCESS,
    MENU_ADMIN_BILLING,
    MENU_ADMIN_BROADCASTS,
    MENU_ADMIN_HOME,
    MENU_ADMIN_PROMOS,
    MENU_ADMIN_SUPPORT,
    MENU_ADMIN_USERS,
    MENU_HOME,
)


def build_admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎛 Режим работы", callback_data=MENU_ADMIN_ACCESS),
                InlineKeyboardButton(text="💳 Биллинг", callback_data=MENU_ADMIN_BILLING),
            ],
            [
                InlineKeyboardButton(text="👥 Пользователи", callback_data=MENU_ADMIN_USERS),
                InlineKeyboardButton(text="🎁 Промокоды", callback_data=MENU_ADMIN_PROMOS),
            ],
            [
                InlineKeyboardButton(text="📢 Рассылки", callback_data=MENU_ADMIN_BROADCASTS),
                InlineKeyboardButton(text="🛟 Support Desk", callback_data=MENU_ADMIN_SUPPORT),
            ],
            [
                InlineKeyboardButton(text="⬅️ Вернуться в клиентское меню", callback_data=MENU_HOME),
            ],
        ]
    )


def build_admin_section_menu(*, action_text: str, action_callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=action_text, callback_data=action_callback)],
            [InlineKeyboardButton(text="⬅️ Вернуться в админку", callback_data=MENU_ADMIN_HOME)],
        ]
    )


def build_access_mode_menu(*, current_mode: AccessMode) -> InlineKeyboardMarkup:
    free_label = (
        "🟢 Бесплатная выдача"
        if current_mode is AccessMode.FREE_ACCESS
        else "⚪ Бесплатная выдача"
    )
    billing_label = (
        "🟢 Биллинг активен"
        if current_mode is AccessMode.BILLING_ENABLED
        else "⚪ Биллинг активен"
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=free_label, callback_data=ACTION_ADMIN_SET_FREE_ACCESS)],
            [
                InlineKeyboardButton(
                    text=billing_label,
                    callback_data=ACTION_ADMIN_SET_BILLING_ENABLED,
                )
            ],
            [InlineKeyboardButton(text="⬅️ Вернуться в админку", callback_data=MENU_ADMIN_HOME)],
        ]
    )


def build_admin_users_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔎 Найти пользователя",
                    callback_data=ACTION_ADMIN_USERS_SEARCH,
                ),
                InlineKeyboardButton(
                    text="🔄 Обновить",
                    callback_data=ACTION_ADMIN_USERS_REFRESH,
                ),
            ],
            [InlineKeyboardButton(text="⬅️ Вернуться в админку", callback_data=MENU_ADMIN_HOME)],
        ]
    )


def build_admin_users_overview_menu(
    *,
    users: tuple[UserSummary, ...],
    current_page: int,
    has_next_page: bool,
    current_filter: AdminUsersFilter,
) -> InlineKeyboardMarkup:
    inline_keyboard: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text=_build_filter_label(AdminUsersFilter.ALL, current_filter),
                callback_data=f"{ADMIN_USERS_FILTER_PREFIX}{AdminUsersFilter.ALL}",
            ),
            InlineKeyboardButton(
                text=_build_filter_label(AdminUsersFilter.WITH_ACCESS, current_filter),
                callback_data=f"{ADMIN_USERS_FILTER_PREFIX}{AdminUsersFilter.WITH_ACCESS}",
            ),
            InlineKeyboardButton(
                text=_build_filter_label(AdminUsersFilter.WITHOUT_ACCESS, current_filter),
                callback_data=f"{ADMIN_USERS_FILTER_PREFIX}{AdminUsersFilter.WITHOUT_ACCESS}",
            ),
        ]
    ]
    for user in users:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=_build_user_button_label(user),
                    callback_data=f"{ADMIN_USER_VIEW_PREFIX}{user.telegram_id}",
                )
            ]
        )

    pagination_row = []
    if current_page > 0:
        pagination_row.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"{ADMIN_USERS_PAGE_PREFIX}{current_filter}:{current_page - 1}",
            )
        )
    if has_next_page:
        pagination_row.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=f"{ADMIN_USERS_PAGE_PREFIX}{current_filter}:{current_page + 1}",
            )
        )
    if pagination_row:
        inline_keyboard.append(pagination_row)

    inline_keyboard.extend(build_admin_users_menu().inline_keyboard)
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_admin_user_detail_menu(detail: AdminUserDetail) -> InlineKeyboardMarkup:
    telegram_id = detail.user.telegram_id
    inline_keyboard = []
    if detail.vpn_access is None or detail.vpn_access.status != "active":
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=(
                        "✅ Включить доступ"
                        if detail.vpn_access is not None
                        else "⚡ Выдать доступ"
                    ),
                    callback_data=f"{ADMIN_USER_ISSUE_PREFIX}{telegram_id}",
                )
            ]
        )
    else:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="🔗 Открыть доступ",
                    callback_data=f"{ADMIN_USER_OPEN_ACCESS_PREFIX}{telegram_id}",
                )
            ]
        )
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="♻️ Перевыпустить доступ",
                    callback_data=f"{ADMIN_USER_REISSUE_PREFIX}{telegram_id}",
                ),
                InlineKeyboardButton(
                    text="⛔ Отключить доступ",
                    callback_data=f"{ADMIN_USER_DISABLE_PREFIX}{telegram_id}",
                ),
            ]
        )

    inline_keyboard.extend(
        [
            [
                InlineKeyboardButton(
                    text="🕓 История доступа",
                    callback_data=f"{ADMIN_USER_HISTORY_PREFIX}{telegram_id}",
                )
            ],
            [InlineKeyboardButton(text="⬅️ К пользователям", callback_data=MENU_ADMIN_USERS)],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_admin_user_access_menu(
    *,
    subscription_url: str,
    telegram_id: int,
) -> InlineKeyboardMarkup:
    inline_keyboard = []
    if subscription_url.startswith(("http://", "https://")):
        inline_keyboard.append(
            [InlineKeyboardButton(text="🔗 Открыть подписку", url=subscription_url)]
        )
    inline_keyboard.extend(
        [
            [
                InlineKeyboardButton(
                    text="⬅️ В карточку пользователя",
                    callback_data=f"{ADMIN_USER_VIEW_PREFIX}{telegram_id}",
                )
            ],
            [InlineKeyboardButton(text="⬅️ К пользователям", callback_data=MENU_ADMIN_USERS)],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def _build_user_button_label(user: UserSummary) -> str:
    if user.first_name:
        return user.first_name[:24]
    if user.username:
        return f"@{user.username}"[:24]
    return str(user.telegram_id)


def _build_filter_label(
    target_filter: AdminUsersFilter,
    current_filter: AdminUsersFilter,
) -> str:
    label = {
        AdminUsersFilter.ALL: "Все",
        AdminUsersFilter.WITH_ACCESS: "С доступом",
        AdminUsersFilter.WITHOUT_ACCESS: "Без доступа",
    }[target_filter]
    prefix = "🟢 " if target_filter is current_filter else "⚪ "
    return f"{prefix}{label}"
