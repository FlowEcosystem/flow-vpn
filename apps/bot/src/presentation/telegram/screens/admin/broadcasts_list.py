from src.application.broadcasts.dto import BroadcastSummary

from .broadcasts_common import format_broadcast_line


def build_admin_broadcasts_text(broadcasts: tuple[BroadcastSummary, ...]) -> str:
    if not broadcasts:
        history_block = "Рассылок пока не было."
    else:
        history_block = "\n".join(format_broadcast_line(b) for b in broadcasts)

    return (
        "📢 <b>Рассылки</b>\n\n"
        f"Последние: <b>{len(broadcasts)}</b>\n\n"
        f"{history_block}"
    )
