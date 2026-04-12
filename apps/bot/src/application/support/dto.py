from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SupportOverview:
    support_url: str | None
    support_title: str
