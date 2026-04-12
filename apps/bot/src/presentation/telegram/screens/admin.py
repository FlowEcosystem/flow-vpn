# ruff: noqa: RUF001

from datetime import UTC

from src.application.admin import AdminDashboard
from src.application.admin.dto import (
    AdminUserDetail,
    AdminUserSearchResult,
    AdminUsersFilter,
    AdminUsersOverview,
)
from src.application.runtime import AccessMode
from src.application.users import UserSummary
from src.application.vpn import VpnAccess, VpnAccessEvent
from src.presentation.telegram.callbacks import (
    ACTION_ADMIN_ACCESS,
    ACTION_ADMIN_BILLING,
    ACTION_ADMIN_BROADCASTS,
    ACTION_ADMIN_PROMOS,
    ACTION_ADMIN_SUPPORT,
    ACTION_ADMIN_USERS,
    MENU_ADMIN_ACCESS,
    MENU_ADMIN_BILLING,
    MENU_ADMIN_BROADCASTS,
    MENU_ADMIN_PROMOS,
    MENU_ADMIN_SUPPORT,
    MENU_ADMIN_USERS,
)
from src.presentation.telegram.screens.start import SectionScreen


def format_access_mode(access_mode: AccessMode) -> str:
    if access_mode is AccessMode.FREE_ACCESS:
        return "🎁 Бесплатная выдача"

    return "💳 Биллинг активен"


def build_access_mode_text(access_mode: AccessMode) -> str:
    return (
        "🎛 <b>Режим работы</b>\n\n"
        f"Текущий режим: <b>{format_access_mode(access_mode)}</b>\n\n"
        "Этот переключатель управляет тем,"
        " как бот ведёт пользователя в сценарии подключения.\n\n"
        "• <b>Бесплатная выдача</b> — доступ отдаётся сразу\n"
        "• <b>Биллинг активен</b> — пользователь идёт в платный flow\n\n"
        "Изменение применяется сразу после выбора."
    )


def build_admin_home_text(display_name: str, dashboard: AdminDashboard) -> str:
    return (
        "🛠 <b>Control Panel • Flow VPN</b>\n"
        f"Управляющий профиль: <b>{display_name}</b>\n\n"
        "Актуальная сводка по продукту:\n"
        f"• Режим доступа: <b>{format_access_mode(dashboard.access_mode)}</b>\n"
        f"• Пользователей в базе: <b>{dashboard.total_users}</b>\n"
        f"• Новых за сегодня: <b>{dashboard.new_users_today}</b>\n"
        f"• Telegram Premium: <b>{dashboard.premium_users}</b>\n\n"
        "Ниже собраны ключевые операционные разделы:"
        " доступ, биллинг, аудитория, промо, коммуникации и support."
    )


def build_admin_users_text(overview: AdminUsersOverview) -> str:
    recent_users_block = (
        "\n".join(_format_admin_user_line(user) for user in overview.recent_users)
        if overview.recent_users
        else "• Пока пользователей нет"
    )
    return (
        "👥 <b>Пользователи</b>\n\n"
        f"• Всего пользователей: <b>{overview.total_users}</b>\n"
        f"• С активным доступом: <b>{overview.users_with_access}</b>\n\n"
        f"• Сегмент: <b>{_format_users_filter(overview.current_filter)}</b>\n"
        f"• Страница: <b>{overview.current_page + 1}</b>\n"
        f"• В выборке: <b>{overview.total_filtered}</b>\n\n"
        "Последние регистрации:\n"
        f"{recent_users_block}\n\n"
        "Используйте поиск ниже, чтобы быстро найти пользователя"
        " по Telegram ID, @username или имени."
    )


def build_admin_users_search_prompt_text() -> str:
    return (
        "🔎 <b>Поиск пользователя</b>\n\n"
        "Отправьте одним сообщением:\n"
        "• <b>Telegram ID</b>\n"
        "• <b>@username</b>\n"
        "• или часть имени\n\n"
        "Я покажу подходящих пользователей из базы."
    )


def build_admin_users_search_result_text(result: AdminUserSearchResult) -> str:
    users_block = (
        "\n".join(_format_admin_user_line(user) for user in result.users)
        if result.users
        else "• Ничего не найдено"
    )
    return (
        "🔎 <b>Результаты поиска</b>\n\n"
        f"Запрос: <b>{result.query}</b>\n\n"
        f"{users_block}\n\n"
        "Можно отправить новый запрос или вернуться в экран пользователей."
    )


def build_admin_user_detail_text(detail: AdminUserDetail) -> str:
    display_name = _resolve_display_name_from_profile(detail)
    username = f"@{detail.user.username}" if detail.user.username else "без username"
    premium = "есть" if detail.user.is_premium else "нет"
    created_at = detail.user.created_at.astimezone(UTC).strftime("%d.%m.%Y")
    access_block = (
        _format_admin_user_access_block(detail.vpn_access)
        if detail.vpn_access is not None
        else "• Статус доступа: <b>не выдан</b>\n"
    )
    return (
        f"👤 <b>{display_name}</b>\n\n"
        f"• Username: <b>{username}</b>\n"
        f"• Telegram ID: <code>{detail.user.telegram_id}</code>\n"
        f"• Telegram Premium: <b>{premium}</b>\n"
        f"• Зарегистрирован: <b>{created_at}</b>\n"
        f"{access_block}\n"
        "Выберите действие ниже."
    )


def build_admin_user_access_text(detail: AdminUserDetail) -> str:
    if detail.vpn_access is None:
        return (
            "🔗 <b>Доступ пользователя</b>\n\n"
            "У этого пользователя пока нет активного доступа."
        )

    access = detail.vpn_access
    issued_at = access.issued_at.astimezone(UTC).strftime("%d.%m.%Y %H:%M UTC")
    expires_at = (
        access.expires_at.astimezone(UTC).strftime("%d.%m.%Y %H:%M UTC")
        if access.expires_at is not None
        else "без ограничения"
    )
    return (
        "🔗 <b>Активный доступ</b>\n\n"
        f"• Профиль: <b>{access.external_username}</b>\n"
        f"• Статус: <b>{_format_access_status(access.status)}</b>\n"
        f"• Выдан: <b>{issued_at}</b>\n"
        f"• Действует до: <b>{expires_at}</b>\n"
        f"• Ссылок: <b>{len(access.vless_links)}</b>\n\n"
        "Открыть подписку можно по кнопке ниже."
    )


def build_admin_user_history_text(detail: AdminUserDetail) -> str:
    display_name = _resolve_display_name_from_profile(detail)
    history_block = (
        "\n".join(_format_access_event(event) for event in detail.history)
        if detail.history
        else "• История пока пуста"
    )
    return (
        f"🕓 <b>История доступа • {display_name}</b>\n\n"
        f"{history_block}\n\n"
        "Здесь отображаются последние изменения по доступу пользователя."
    )


def _format_admin_user_line(user: UserSummary) -> str:
    display_name = _resolve_display_name(user)
    username = f"@{user.username}" if user.username else "без username"
    premium = "⭐" if user.is_premium else ""
    access = "🟢 доступ" if user.has_vpn_access else "⚪ без доступа"
    created_at = user.created_at.astimezone(UTC).strftime("%d.%m")
    suffix = f" {premium}".rstrip()
    return (
        f"• <b>{display_name}</b>{suffix}\n"
        f"  {username} • ID <code>{user.telegram_id}</code> • {access} • {created_at}"
    )


def _resolve_display_name(user: UserSummary) -> str:
    parts = [part for part in (user.first_name, user.last_name) if part]
    if parts:
        return " ".join(parts)
    if user.username:
        return user.username
    return f"User {user.telegram_id}"


def _resolve_display_name_from_profile(detail: AdminUserDetail) -> str:
    parts = [part for part in (detail.user.first_name, detail.user.last_name) if part]
    if parts:
        return " ".join(parts)
    if detail.user.username:
        return detail.user.username
    return f"User {detail.user.telegram_id}"


def _format_admin_user_access_block(access: VpnAccess) -> str:
    issued_at = access.issued_at.astimezone(UTC).strftime("%d.%m.%Y %H:%M")
    return (
        f"• Статус доступа: <b>{_format_access_status(access.status)}</b>\n"
        f"• Профиль: <b>{access.external_username}</b>\n"
        f"• Обновлён: <b>{issued_at}</b>\n"
    )


def _format_access_event(event: VpnAccessEvent) -> str:
    created_at = event.created_at.astimezone(UTC).strftime("%d.%m %H:%M")
    event_title = {
        "issued": "Выдан через пользовательский flow",
        "issued_by_admin": "Выдан администратором",
        "enabled_by_admin": "Снова включён администратором",
        "disabled_by_admin": "Отключён администратором",
        "reissued_by_admin": "Перевыпущен администратором",
    }.get(event.event_type, event.event_type)
    actor = (
        f" • admin {event.actor_telegram_id}"
        if event.actor_telegram_id is not None
        else ""
    )
    return f"• <b>{event_title}</b> • {created_at}{actor}"


def _format_access_status(status: str) -> str:
    return {
        "active": "активен",
        "disabled": "отключён",
    }.get(status, status)


def _format_users_filter(value: AdminUsersFilter) -> str:
    return {
        AdminUsersFilter.ALL: "все пользователи",
        AdminUsersFilter.WITH_ACCESS: "только с доступом",
        AdminUsersFilter.WITHOUT_ACCESS: "без доступа",
    }[value]


ADMIN_SECTION_SCREENS = {
    MENU_ADMIN_ACCESS: SectionScreen(
        text=(
            "🎛 <b>Режим работы</b>\n\n"
            "Здесь настраивается основной сценарий подключения пользователя.\n\n"
            "От этого раздела зависит,"
            " будет ли доступ выдаваться сразу или через платный flow.\n\n"
            "Ключевая точка управления продуктом на старте."
        ),
        action_text="⚙️ Открыть настройки режима",
        action_callback=ACTION_ADMIN_ACCESS,
    ),
    MENU_ADMIN_BILLING: SectionScreen(
        text=(
            "💳 <b>Биллинг</b>\n\n"
            "Здесь будет собран платёжный контур продукта:\n"
            "тарифы, оплаты, статусы и ручные операции.\n\n"
            "Раздел для управления коммерческим сценарием"
            " и контроля платного доступа."
        ),
        action_text="💼 Открыть биллинг",
        action_callback=ACTION_ADMIN_BILLING,
    ),
    MENU_ADMIN_USERS: SectionScreen(
        text=(
            "👥 <b>Пользователи</b>\n\n"
            "Здесь будет центр управления аудиторией:\n"
            "поиск, карточка пользователя, доступы, статусы и ручные действия.\n\n"
            "Главный операционный экран для ежедневной работы команды."
        ),
        action_text="🔎 Открыть пользователей",
        action_callback=ACTION_ADMIN_USERS,
    ),
    MENU_ADMIN_PROMOS: SectionScreen(
        text=(
            "🎁 <b>Промокоды</b>\n\n"
            "Здесь будет управление промо-механикой:\n"
            "создание кодов, лимиты, сроки действия и активации.\n\n"
            "Подходит для маркетинга, бонусных кампаний и ручных компенсаций."
        ),
        action_text="🏷 Открыть промокоды",
        action_callback=ACTION_ADMIN_PROMOS,
    ),
    MENU_ADMIN_BROADCASTS: SectionScreen(
        text=(
            "📢 <b>Рассылки</b>\n\n"
            "Здесь появится центр коммуникаций:\n"
            "анонсы, onboarding, обновления сервиса и ручные сообщения по сегментам.\n\n"
            "Отдельный инструмент для точечной и массовой коммуникации."
        ),
        action_text="✉️ Открыть рассылки",
        action_callback=ACTION_ADMIN_BROADCASTS,
    ),
    MENU_ADMIN_SUPPORT: SectionScreen(
        text=(
            "🛟 <b>Support Desk</b>\n\n"
            "Здесь будет support-поток:\n"
            "обращения, быстрые ответы, эскалации и ручное сопровождение.\n\n"
            "Операционный экран для контроля качества сервиса и скорости реакции."
        ),
        action_text="💬 Открыть support desk",
        action_callback=ACTION_ADMIN_SUPPORT,
    ),
}


ADMIN_ACTION_FEEDBACK = {
    ACTION_ADMIN_ACCESS: "Настройки режима скоро станут глубже 🎛",
    ACTION_ADMIN_BILLING: "Биллинг-раздел скоро станет доступен 💳",
    ACTION_ADMIN_USERS: "Раздел пользователей скоро появится 👥",
    ACTION_ADMIN_PROMOS: "Промокоды скоро будут доступны 🎁",
    ACTION_ADMIN_BROADCASTS: "Раздел рассылок скоро появится 📢",
    ACTION_ADMIN_SUPPORT: "Support Desk скоро станет доступен 🛟",
}
