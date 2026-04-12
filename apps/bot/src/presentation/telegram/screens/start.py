# ruff: noqa: RUF001

from dataclasses import dataclass
from datetime import UTC

from src.application.account import TelegramAccountOverview
from src.application.runtime import AccessMode
from src.application.vpn import VpnAccess
from src.presentation.telegram.callbacks import ACTION_BUY, MENU_BUY


@dataclass(slots=True, frozen=True)
class SectionScreen:
    text: str
    action_text: str
    action_callback: str


def build_home_text(display_name: str, *, is_new_user: bool) -> str:
    if is_new_user:
        return (
            f"👋 <b>Привет, {display_name}!</b>\n\n"
            "Добро пожаловать в <b>Flow VPN</b> ✨\n\n"
            "Быстрый доступ, понятное управление и поддержка без лишнего шума.\n"
            "Всё важное уже собрано в одном аккуратном пространстве.\n\n"
            "Выберите нужный раздел ниже и начнём 🚀"
        )

    return (
        f"✨ <b>С возвращением, {display_name}!</b>\n\n"
        "<b>Flow VPN</b> уже готов к работе.\n"
        "Подключение, кабинет, бонусы и помощь всегда под рукой.\n\n"
        "Выберите нужный раздел ниже 👇"
    )


def build_buy_screen(access_mode: AccessMode) -> SectionScreen:
    if access_mode is AccessMode.FREE_ACCESS:
        return SectionScreen(
            text=(
                "⚡ <b>Подключение к Flow VPN</b>\n\n"
                "Сейчас доступ можно получить <b>сразу и бесплатно</b> 🎁\n\n"
                "Мы подготовим подключение автоматически,"
                " а вам останется открыть ссылку и добавить его в приложение.\n\n"
                "Быстро, аккуратно и без лишних шагов."
            ),
            action_text="🚀 Получить доступ",
            action_callback=ACTION_BUY,
        )

    return SectionScreen(
        text=(
            "⚡ <b>Подключение к Flow VPN</b>\n\n"
            "Сейчас подключение оформляется <b>по подписке</b> 💳\n\n"
            "Здесь скоро появятся тарифы, удобная оплата"
            " и мгновенная активация доступа.\n\n"
            "Всё будет оформляться в несколько понятных шагов."
        ),
        action_text="💳 Открыть тарифы",
        action_callback=ACTION_BUY,
    )


def build_account_screen(account: TelegramAccountOverview) -> SectionScreen:
    registered_at = account.created_at.astimezone(UTC).strftime("%d.%m.%Y")
    access_hint = (
        "Можно открыть доступ ниже."
        if account.vpn_access
        else "Можно подключить VPN в один шаг."
    )
    access_block = (
        (
            "• Статус доступа: <b>активен</b>\n"
            "• Подключение уже готово и доступно в один тап\n\n"
        )
        if account.vpn_access
        else "• Статус доступа: <b>ещё не подключён</b>\n\n"
    )

    return SectionScreen(
        text=(
            "👤 <b>Личный кабинет</b>\n\n"
            f"• Аккаунт активен с <b>{registered_at}</b>\n"
            f"{access_block}"
            "Здесь собрана вся важная информация по вашему доступу.\n"
            f"{access_hint}"
        ),
        action_text=(
            "⚙️ Управлять подключением"
            if account.vpn_access
            else "⚡ Подключить VPN"
        ),
        action_callback=MENU_BUY,
    )


def build_vpn_access_text(access: VpnAccess) -> str:
    expires_at = (
        access.expires_at.astimezone(UTC).strftime("%d.%m.%Y")
        if access.expires_at is not None
        else "без ограничений"
    )
    return (
        "✅ <b>Доступ готов</b>\n\n"
        "Подключение уже готово 🙌\n"
        "Откройте ссылку ниже, чтобы добавить VPN в приложение и начать работу.\n\n"
        f"• Доступ действует: <b>{expires_at}</b>\n\n"
        "Если понадобится, вы всегда сможете вернуться в кабинет."
    )
