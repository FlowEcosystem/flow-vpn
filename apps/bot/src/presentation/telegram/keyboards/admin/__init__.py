"""Admin keyboard composition."""

from .broadcasts import (
    build_admin_broadcast_confirm_menu,
    build_admin_broadcast_segment_menu,
    build_admin_broadcast_text_cancel_menu,
    build_admin_broadcasts_menu,
)
from .bulk import (
    build_admin_users_bulk_actions_menu,
    build_admin_users_bulk_delete_confirm_menu,
    build_admin_users_bulk_history_detail_menu,
    build_admin_users_bulk_history_menu,
    build_admin_users_bulk_issue_confirm_menu,
    build_admin_users_bulk_menu,
    build_admin_users_bulk_operation_status_menu,
    build_admin_users_bulk_progress_menu,
    build_admin_users_bulk_result_menu,
    build_admin_users_bulk_disable_confirm_menu,
    build_admin_users_global_bulk_actions_menu,
    build_admin_users_global_bulk_delete_confirm_menu,
    build_admin_users_global_bulk_issue_confirm_menu,
    build_admin_users_global_bulk_disable_confirm_menu,
)
from .home import build_access_mode_menu, build_admin_menu, build_admin_section_menu
from .promos import (
    build_admin_promo_create_cancel_menu,
    build_admin_promo_detail_menu,
    build_admin_promo_scope_menu,
    build_admin_promo_type_menu,
    build_admin_promos_list_menu,
)
from .support import (
    build_admin_support_reply_cancel_menu,
    build_admin_support_ticket_detail_menu,
    build_admin_support_tickets_menu,
)
from .users import (
    build_admin_user_access_menu,
    build_admin_user_detail_menu,
    build_admin_users_menu,
    build_admin_users_overview_menu,
)

__all__ = [
    "build_access_mode_menu",
    "build_admin_broadcast_confirm_menu",
    "build_admin_broadcast_segment_menu",
    "build_admin_broadcast_text_cancel_menu",
    "build_admin_broadcasts_menu",
    "build_admin_menu",
    "build_admin_promo_create_cancel_menu",
    "build_admin_promo_detail_menu",
    "build_admin_promo_scope_menu",
    "build_admin_promo_type_menu",
    "build_admin_promos_list_menu",
    "build_admin_section_menu",
    "build_admin_support_reply_cancel_menu",
    "build_admin_support_ticket_detail_menu",
    "build_admin_support_tickets_menu",
    "build_admin_user_access_menu",
    "build_admin_user_detail_menu",
    "build_admin_users_bulk_actions_menu",
    "build_admin_users_bulk_delete_confirm_menu",
    "build_admin_users_bulk_history_detail_menu",
    "build_admin_users_bulk_history_menu",
    "build_admin_users_bulk_issue_confirm_menu",
    "build_admin_users_bulk_menu",
    "build_admin_users_bulk_operation_status_menu",
    "build_admin_users_bulk_progress_menu",
    "build_admin_users_bulk_result_menu",
    "build_admin_users_bulk_disable_confirm_menu",
    "build_admin_users_global_bulk_actions_menu",
    "build_admin_users_global_bulk_delete_confirm_menu",
    "build_admin_users_global_bulk_issue_confirm_menu",
    "build_admin_users_global_bulk_disable_confirm_menu",
    "build_admin_users_menu",
    "build_admin_users_overview_menu",
]
