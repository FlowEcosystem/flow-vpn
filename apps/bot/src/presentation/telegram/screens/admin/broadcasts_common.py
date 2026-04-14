from src.application.broadcasts.dto import BroadcastSummary
from src.presentation.telegram.datetime import format_datetime_msk


def format_segment_label(segment: str) -> str:
    return {
        "all": "все пользователи",
        "with_access": "с доступом",
        "without_access": "без доступа",
    }.get(segment, segment)


def format_broadcast_line(broadcast: BroadcastSummary) -> str:
    segment = format_segment_label(broadcast.target_segment)
    created = format_datetime_msk(broadcast.created_at)
    status_icon = {"sending": "⏳", "done": "✅", "failed": "❌"}.get(broadcast.status, "⏳")
    stats = (
        f"{broadcast.sent_count}✓ {broadcast.failed_count}✗"
        if broadcast.status == "done"
        else broadcast.status
    )
    return f"{status_icon} {created} · {segment} · {stats}"
