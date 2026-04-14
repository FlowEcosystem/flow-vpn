from uuid import UUID


def parse_ticket_id(callback_data: str, prefix: str) -> UUID | None:
    raw_id = callback_data.removeprefix(prefix)
    try:
        return UUID(raw_id)
    except ValueError:
        return None
