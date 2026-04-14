from datetime import datetime, timedelta, timezone

MSK = timezone(timedelta(hours=3), name="MSK")


def to_msk(dt: datetime) -> datetime:
    return dt.astimezone(MSK)


def format_datetime_msk(dt: datetime, *, include_tz: bool = True) -> str:
    formatted = to_msk(dt).strftime("%d.%m.%Y %H:%M")
    return f"{formatted}" if include_tz else formatted


def format_expiration_msk(dt: datetime | None) -> str:
    if dt is None:
        return "бессрочно"
    return format_datetime_msk(dt)
