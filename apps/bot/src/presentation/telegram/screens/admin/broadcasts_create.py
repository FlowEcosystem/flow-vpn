from .broadcasts_common import format_segment_label


def build_admin_broadcast_segment_text() -> str:
    return "📢 <b>Новая рассылка — шаг 1/2</b>\n\nВыберите аудиторию:"


def build_admin_broadcast_text_prompt(segment_label: str) -> str:
    return (
        f"📢 <b>Новая рассылка — шаг 2/2</b>\n\n"
        f"Аудитория: <b>{segment_label}</b>\n\n"
        "Введите текст сообщения (поддерживается HTML-разметка):"
    )


def build_admin_broadcast_preview_text(segment_label: str, text: str) -> str:
    preview = text[:500] + ("…" if len(text) > 500 else "")
    return (
        "📢 <b>Предпросмотр рассылки</b>\n\n"
        f"• Аудитория: <b>{segment_label}</b>\n\n"
        f"<b>Текст:</b>\n{preview}\n\n"
        "Нажмите <b>Запустить</b>, чтобы начать рассылку."
    )


def build_admin_broadcast_launched_text(
    segment_label: str,
    recipient_count: int,
) -> str:
    return (
        "📢 <b>Рассылка запущена</b>\n\n"
        f"• Аудитория: <b>{segment_label}</b>\n"
        f"• Получателей: <b>{recipient_count}</b>\n\n"
        "Сообщения отправляются в фоне."
    )
