# ruff: noqa: RUF001

from src.application.admin.dto import AdminUsersOverview

from .bulk_common import format_users_filter


def build_admin_users_bulk_delete_confirm_text(overview: AdminUsersOverview) -> str:
    filter_label = format_users_filter(overview.current_filter)
    return (
        "⚠️ <b>Подтвердите массовое удаление</b>\n\n"
        "Будут удалены <b>все подписки</b> у пользователей на текущей странице.\n\n"
        f"• Сегмент: <b>{filter_label}</b>\n"
        f"• Страница: <b>{overview.current_page + 1}</b>\n"
        f"• Пользователей в выборке: <b>{len(overview.recent_users)}</b>\n\n"
        "Действие необратимо."
    )


def build_admin_users_bulk_actions_text(overview: AdminUsersOverview) -> str:
    filter_label = format_users_filter(overview.current_filter)
    return (
        "⚙️ <b>Массовые действия</b>\n\n"
        "Операции ниже применяются только к пользователям на текущей странице списка.\n\n"
        f"• Сегмент: <b>{filter_label}</b>\n"
        f"• Страница: <b>{overview.current_page + 1}</b>\n"
        f"• Пользователей в выборке: <b>{len(overview.recent_users)}</b>\n\n"
        "Выберите нужное действие."
    )


def build_admin_users_global_bulk_actions_text(overview: AdminUsersOverview) -> str:
    filter_label = format_users_filter(overview.current_filter)
    return (
        "🌐 <b>Массовые действия над всеми пользователями</b>\n\n"
        "Операции ниже применяются ко <b>всему текущему сегменту</b>, а не только к открытой странице.\n\n"
        f"• Сегмент: <b>{filter_label}</b>\n"
        f"• Всего пользователей в сегменте: <b>{overview.total_filtered:,}</b>\n"
        f"• Текущая страница для возврата: <b>{overview.current_page + 1}</b>\n\n"
        "Выберите нужное действие."
    )


def build_admin_users_bulk_disable_confirm_text(overview: AdminUsersOverview) -> str:
    filter_label = format_users_filter(overview.current_filter)
    return (
        "⚠️ <b>Подтвердите массовое отключение</b>\n\n"
        "Будут отключены <b>все активные подписки</b> у пользователей на текущей странице.\n\n"
        f"• Сегмент: <b>{filter_label}</b>\n"
        f"• Страница: <b>{overview.current_page + 1}</b>\n"
        f"• Пользователей в выборке: <b>{len(overview.recent_users)}</b>\n\n"
        "Подписки не удаляются, их можно будет включить обратно."
    )


def build_admin_users_bulk_issue_confirm_text(overview: AdminUsersOverview) -> str:
    filter_label = format_users_filter(overview.current_filter)
    return (
        "⚠️ <b>Подтвердите массовую выдачу</b>\n\n"
        "Каждому пользователю на текущей странице будет выдана <b>новая подписка</b>.\n\n"
        f"• Сегмент: <b>{filter_label}</b>\n"
        f"• Страница: <b>{overview.current_page + 1}</b>\n"
        f"• Пользователей в выборке: <b>{len(overview.recent_users)}</b>\n\n"
        "Это действие добавит новые подписки и увеличит их количество у пользователей."
    )


def build_admin_users_global_bulk_delete_confirm_text(overview: AdminUsersOverview) -> str:
    filter_label = format_users_filter(overview.current_filter)
    return (
        "⚠️ <b>Подтвердите массовое удаление</b>\n\n"
        "Будут удалены <b>все подписки</b> у всех пользователей текущего сегмента.\n\n"
        f"• Сегмент: <b>{filter_label}</b>\n"
        f"• Пользователей в сегменте: <b>{overview.total_filtered:,}</b>\n\n"
        "Действие необратимо."
    )


def build_admin_users_global_bulk_disable_confirm_text(overview: AdminUsersOverview) -> str:
    filter_label = format_users_filter(overview.current_filter)
    return (
        "⚠️ <b>Подтвердите массовое отключение</b>\n\n"
        "Будут отключены <b>все активные подписки</b> у всех пользователей текущего сегмента.\n\n"
        f"• Сегмент: <b>{filter_label}</b>\n"
        f"• Пользователей в сегменте: <b>{overview.total_filtered:,}</b>\n\n"
        "Подписки не удаляются, их можно будет включить обратно."
    )


def build_admin_users_global_bulk_issue_confirm_text(overview: AdminUsersOverview) -> str:
    filter_label = format_users_filter(overview.current_filter)
    return (
        "⚠️ <b>Подтвердите массовую выдачу</b>\n\n"
        "Каждому пользователю текущего сегмента будет выдана <b>новая подписка</b>.\n\n"
        f"• Сегмент: <b>{filter_label}</b>\n"
        f"• Пользователей в сегменте: <b>{overview.total_filtered:,}</b>\n\n"
        "Это действие добавит новые подписки и увеличит их количество у пользователей."
    )
