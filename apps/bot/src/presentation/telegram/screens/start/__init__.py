# ruff: noqa: RUF001

from dataclasses import dataclass

from src.application.account import TelegramAccountOverview
from src.application.runtime import AccessMode
from src.application.vpn import VpnAccess
from src.presentation.telegram.callbacks import ACTION_BUY, MENU_BUY
from src.presentation.telegram.datetime import format_datetime_msk, format_expiration_msk


@dataclass(slots=True, frozen=True)
class SectionScreen:
    text: str
    action_text: str
    action_callback: str


def build_home_text(display_name: str, *, is_new_user: bool) -> str:
    if is_new_user:
        return (
            f"👋 <b>Привет, {display_name}!</b>\n\n"
            "Добро пожаловать в <b>Flow VPN</b> — быстрый и надёжный VPN.\n\n"
            "⚡️ Подключение за 30 секунд\n"
            "🌍 Без ограничений и блокировок\n"
            "🔒 Зашифрованный трафик\n\n"
            "Нажми <b>Кабинет</b> — и ты уже в сети."
        )

    return (
        f"👋 <b>{display_name}</b>, с возвращением!\n\n"
        "Управляй подключением в <b>Кабинете</b>."
    )


def build_buy_screen(access_mode: AccessMode) -> SectionScreen:
    if access_mode is AccessMode.FREE_ACCESS:
        return SectionScreen(
            text=(
                "⚡ <b>Подключение к VPN</b>\n\n"
                "Сейчас доступ выдаётся <b>бесплатно</b>.\n"
                "Нажми кнопку — конфиг будет готов за несколько секунд."
            ),
            action_text="⚡ Получить доступ",
            action_callback=ACTION_BUY,
        )

    return SectionScreen(
        text=(
            "⚡ <b>Подключение к VPN</b>\n\n"
            "Платные тарифы пока в разработке.\n"
            "Нужен доступ прямо сейчас — напиши в поддержку."
        ),
        action_text="🛟 Поддержка",
        action_callback=ACTION_BUY,
    )


def build_account_screen(account: TelegramAccountOverview) -> SectionScreen:
    return SectionScreen(
        text=(
            "👤 <b>Кабинет</b>\n\n"
            "Подписок пока нет.\n"
            "Подключение бесплатное — займёт меньше минуты."
        ),
        action_text="⚡ Подключить VPN",
        action_callback=MENU_BUY,
    )


def build_vpn_access_text(access: VpnAccess) -> str:
    expires_at = format_expiration_msk(access.expires_at)
    return (
        "✅ <b>VPN подключён!</b>\n\n"
        "Открой ссылку ниже и добавь конфиг в приложение.\n\n"
        f"Действует до: <b>{expires_at}</b>"
    )


def build_subscriptions_list_text(accesses: tuple[VpnAccess, ...]) -> str:
    if not accesses:
        return (
            "👤 <b>Кабинет</b>\n\n"
            "Подписок пока нет.\n"
            "Подключение бесплатное — займёт меньше минуты."
        )

    active_count = sum(1 for a in accesses if a.status == "active")
    inactive_count = len(accesses) - active_count

    if active_count > 0 and inactive_count == 0:
        status_line = f"🟢 Активно: <b>{active_count}</b>"
    elif active_count == 0:
        status_line = "⏸ Все подписки отключены"
    else:
        status_line = f"🟢 Активно: <b>{active_count}</b>  ·  🔴 Отключено: <b>{inactive_count}</b>"

    return f"🔐 <b>Мои подписки</b>\n\n{status_line}"


def build_subscription_detail_text(access: VpnAccess, index: int) -> str:
    status_line = "🟢 <b>Активна</b>" if access.status == "active" else "🔴 <b>Отключена</b>"
    expires_at = format_expiration_msk(access.expires_at)
    issued_at = format_datetime_msk(access.issued_at)
    return (
        f"🔐 <b>Подписка #{index}</b>\n\n"
        f"{status_line}\n"
        f"Выдана: {issued_at}  ·  До: {expires_at}"
    )
