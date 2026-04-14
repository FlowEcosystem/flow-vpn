# ruff: noqa: RUF001

from src.application.admin.dto import AdminUsersFilter

from .bulk_common import build_progress_bar, format_users_filter


def build_admin_users_bulk_progress_text(
    *,
    action_title: str,
    current_filter: AdminUsersFilter,
    global_scope: bool,
    total_users: int,
    processed_users: int,
    affected_accesses: int,
    skipped_users: int,
    failed_users: int,
    current_user_telegram_id: int | None = None,
) -> str:
    scope_label = "весь текущий сегмент" if global_scope else "текущая страница"
    percent = 100 if total_users == 0 else min(100, int(processed_users * 100 / total_users))
    bar = build_progress_bar(percent)

    current_line = ""
    if current_user_telegram_id is not None:
        current_line = f"\n• Сейчас: <code>{current_user_telegram_id}</code>"

    return (
        f"⏳ <b>{action_title}</b>\n\n"
        f"• Область: <b>{scope_label}</b>\n"
        f"• Сегмент: <b>{format_users_filter(current_filter)}</b>\n"
        f"• Прогресс: <b>{processed_users:,} / {total_users:,}</b> · <b>{percent}%</b>\n"
        f"<code>{bar}</code>\n\n"
        f"• Изменено подписок: <b>{affected_accesses:,}</b>\n"
        f"• Без изменений: <b>{skipped_users:,}</b>\n"
        f"• Ошибок: <b>{failed_users:,}</b>"
        f"{current_line}\n\n"
        "Операция выполняется. Экран обновляется автоматически."
    )


def build_admin_users_bulk_queued_text(
    *,
    action_title: str,
    current_filter: AdminUsersFilter,
    global_scope: bool,
    total_users: int,
) -> str:
    scope_label = "весь текущий сегмент" if global_scope else "текущая страница"
    return (
        f"🕒 <b>{action_title}</b>\n\n"
        f"• Область: <b>{scope_label}</b>\n"
        f"• Сегмент: <b>{format_users_filter(current_filter)}</b>\n"
        f"• Пользователей в очереди: <b>{total_users:,}</b>\n\n"
        "Операция поставлена в очередь. Воркер подхватит её автоматически, "
        "а этот экран будет обновляться по ходу выполнения."
    )


def build_admin_users_bulk_cancelled_text(
    *,
    action_title: str,
    current_filter: AdminUsersFilter,
    global_scope: bool,
    total_users: int,
    processed_users: int,
    affected_accesses: int,
    skipped_users: int,
    failed_users: int,
) -> str:
    scope_label = "весь текущий сегмент" if global_scope else "текущая страница"
    return (
        f"⛔ <b>{action_title}</b>\n\n"
        f"• Область: <b>{scope_label}</b>\n"
        f"• Сегмент: <b>{format_users_filter(current_filter)}</b>\n"
        f"• Обработано пользователей: <b>{processed_users:,} / {total_users:,}</b>\n"
        f"• Изменено подписок: <b>{affected_accesses:,}</b>\n"
        f"• Без изменений: <b>{skipped_users:,}</b>\n"
        f"• Ошибок: <b>{failed_users:,}</b>\n\n"
        "Операция была остановлена вручную."
    )


def build_admin_users_bulk_result_text(
    *,
    action_title: str,
    current_filter: AdminUsersFilter,
    global_scope: bool,
    total_users: int,
    affected_accesses: int,
    skipped_users: int,
    failed_users: int,
) -> str:
    scope_label = "весь текущий сегмент" if global_scope else "текущая страница"
    successful_users = max(total_users - failed_users, 0)
    return (
        f"✅ <b>{action_title}</b>\n\n"
        f"• Область: <b>{scope_label}</b>\n"
        f"• Сегмент: <b>{format_users_filter(current_filter)}</b>\n"
        f"• Обработано пользователей: <b>{total_users:,}</b>\n"
        f"• Успешно: <b>{successful_users:,}</b>\n"
        f"• Без изменений: <b>{skipped_users:,}</b>\n"
        f"• Ошибок: <b>{failed_users:,}</b>\n"
        f"• Изменено подписок: <b>{affected_accesses:,}</b>\n\n"
        "Можно вернуться к списку или открыть меню массовых действий."
    )


def build_admin_users_bulk_failed_text(
    *,
    action_title: str,
    current_filter: AdminUsersFilter,
    global_scope: bool,
    total_users: int,
    processed_users: int,
    affected_accesses: int,
    skipped_users: int,
    failed_users: int,
    error_message: str | None,
) -> str:
    scope_label = "весь текущий сегмент" if global_scope else "текущая страница"
    details = error_message or "Неизвестная ошибка."
    return (
        f"❌ <b>{action_title}</b>\n\n"
        f"• Область: <b>{scope_label}</b>\n"
        f"• Сегмент: <b>{format_users_filter(current_filter)}</b>\n"
        f"• Обработано пользователей: <b>{processed_users:,} / {total_users:,}</b>\n"
        f"• Изменено подписок: <b>{affected_accesses:,}</b>\n"
        f"• Без изменений: <b>{skipped_users:,}</b>\n"
        f"• Ошибок: <b>{failed_users:,}</b>\n\n"
        f"Причина: <code>{details}</code>"
    )
