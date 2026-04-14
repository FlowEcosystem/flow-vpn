# ruff: noqa: RUF001

from .support_list import build_admin_support_ticket_detail_menu, build_admin_support_tickets_menu
from .support_reply import build_admin_support_reply_cancel_menu

__all__ = [
    "build_admin_support_reply_cancel_menu",
    "build_admin_support_ticket_detail_menu",
    "build_admin_support_tickets_menu",
]
