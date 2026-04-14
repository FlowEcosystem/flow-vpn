# ruff: noqa: RUF001

from src.application.admin import AdminDashboard
from src.application.runtime import AccessMode
from src.presentation.telegram.callbacks import (
    ACTION_ADMIN_ACCESS,
    ACTION_ADMIN_BILLING,
    ACTION_ADMIN_USERS,
    MENU_ADMIN_ACCESS,
    MENU_ADMIN_BILLING,
    MENU_ADMIN_USERS,
)
from src.presentation.telegram.screens.start import SectionScreen


def format_access_mode(access_mode: AccessMode) -> str:
    if access_mode is AccessMode.FREE_ACCESS:
        return "🎁 Бесплатная выдача"
    return "💳 Биллинг"


def format_max_vpn_accesses_per_user(limit: int) -> str:
    if limit <= 0:
        return "без лимита"
    return str(limit)


def build_access_mode_text(access_mode: AccessMode, max_vpn_accesses_per_user: int) -> str:
    mode_label = format_access_mode(access_mode)
    if access_mode is AccessMode.FREE_ACCESS:
        description = "Доступ выдаётся пользователям сразу и бесплатно."
    else:
        description = "Пользователь попадает в платный сценарий подключения."

    return (
        "🎛 <b>Режим работы</b>\n\n"
        f"Текущий режим: <b>{mode_label}</b>\n\n"
        f"• Лимит подписок на пользователя: "
        f"<b>{format_max_vpn_accesses_per_user(max_vpn_accesses_per_user)}</b>\n\n"
        f"{description}\n\n"
        "• <b>Бесплатная выдача</b> — доступ сразу\n"
        "• <b>Биллинг</b> — платный flow\n\n"
        "Изменение вступает в силу немедленно."
    )


def build_admin_home_text(display_name: str, dashboard: AdminDashboard) -> str:
    return (
        "🛠 <b>Flow VPN · Панель управления</b>\n\n"
        f"Привет, {display_name} 👋\n\n"
        "📊 <b>Статистика</b>\n"
        f"• Пользователей: <b>{dashboard.total_users:,}</b>\n"
        f"• Новых сегодня: <b>+{dashboard.new_users_today}</b>\n"
        f"• Telegram Premium: <b>{dashboard.premium_users}</b>\n\n"
        f"⚙️ Режим: <b>{format_access_mode(dashboard.access_mode)}</b>\n"
        f"🔢 Лимит подписок: "
        f"<b>{format_max_vpn_accesses_per_user(dashboard.max_vpn_accesses_per_user)}</b>"
    )


def build_max_vpn_accesses_prompt_text(current_limit: int) -> str:
    return (
        "🔢 <b>Лимит подписок на пользователя</b>\n\n"
        f"Текущее значение: <b>{format_max_vpn_accesses_per_user(current_limit)}</b>\n\n"
        "Отправьте число одним сообщением.\n"
        "• <b>0</b> — без лимита\n"
        "• <b>1..99</b> — максимальное количество подписок"
    )


ADMIN_SECTION_SCREENS = {
    MENU_ADMIN_ACCESS: SectionScreen(
        text=(
            "🎛 <b>Режим работы</b>\n\n"
            "Управляет сценарием подключения: бесплатная выдача или платный flow.\n\n"
            "Изменение применяется мгновенно для всех пользователей."
        ),
        action_text="⚙️ Открыть настройки",
        action_callback=ACTION_ADMIN_ACCESS,
    ),
    MENU_ADMIN_BILLING: SectionScreen(
        text=(
            "💳 <b>Биллинг</b>\n\n"
            "Тарифы, оплаты, статусы и ручные операции.\n\n"
            "Раздел в разработке."
        ),
        action_text="💼 Открыть биллинг",
        action_callback=ACTION_ADMIN_BILLING,
    ),
    MENU_ADMIN_USERS: SectionScreen(
        text=(
            "👥 <b>Пользователи</b>\n\n"
            "Поиск, карточка пользователя, управление доступом.\n\n"
            "Основной операционный экран."
        ),
        action_text="🔎 Открыть список",
        action_callback=ACTION_ADMIN_USERS,
    ),
}


ADMIN_ACTION_FEEDBACK = {
    ACTION_ADMIN_ACCESS: "Раздел настроек режима скоро станет глубже 🎛",
    ACTION_ADMIN_BILLING: "Биллинг в разработке — скоро будет доступен 💳",
    ACTION_ADMIN_USERS: "Раздел пользователей скоро появится 👥",
}
