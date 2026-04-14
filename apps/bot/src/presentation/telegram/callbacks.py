MENU_HOME = "menu:home"
MENU_BUY = "menu:buy"
MENU_ACCOUNT = "menu:account"
MENU_REFER = "menu:refer"
MENU_PROMO = "menu:promo"
MENU_STATUS = "menu:status"
MENU_REVIEWS = "menu:reviews"
MENU_SUPPORT = "menu:support"
MENU_ADMIN_HOME = "admin:home"
MENU_ADMIN_ACCESS = "admin:access"
MENU_ADMIN_BILLING = "admin:billing"
MENU_ADMIN_USERS = "admin:users"
MENU_ADMIN_PROMOS = "admin:promos"
MENU_ADMIN_BROADCASTS = "admin:broadcasts"
MENU_ADMIN_SUPPORT = "admin:support"

ACTION_BUY = "action:buy"
ACTION_ACCOUNT = "action:account"
ACTION_REFER = "action:refer"
ACTION_PROMO = "action:promo"
PROMO_APPLY_PREFIX = "promo:apply:"
PROMO_SELECT_ACCESS_PREFIX = "promo:select_access:"
ACTION_STATUS = "action:status"
ACTION_REVIEWS = "action:reviews"
ACTION_REVIEW_SKIP = "action:review_skip"
ACTION_SUPPORT = "action:support"
ACTION_ADMIN_ACCESS = "admin_action:access"
ACTION_ADMIN_BILLING = "admin_action:billing"
ACTION_ADMIN_USERS = "admin_action:users"
ACTION_ADMIN_PROMOS = "admin_action:promos"
ACTION_ADMIN_BROADCASTS = "admin_action:broadcasts"
ACTION_ADMIN_SUPPORT = "admin_action:support"
ACTION_ADMIN_SET_FREE_ACCESS = "admin_action:set_free_access"
ACTION_ADMIN_SET_BILLING_ENABLED = "admin_action:set_billing_enabled"
ACTION_ADMIN_SET_MAX_VPN_ACCESSES = "admin_action:set_max_vpn_accesses"
ACTION_ADMIN_USERS_SEARCH = "admin_action:users_search"
ACTION_ADMIN_USERS_REFRESH = "admin_action:users_refresh"
REVIEW_RATING_PREFIX = "review:rating:"
SUPPORT_RATING_PREFIX = "support:rating:"
USER_ACCESS_VIEW_PREFIX = "user_access:view:"
USER_ACCESS_ENABLE_PREFIX = "user_access:enable:"
USER_ACCESS_DISABLE_PREFIX = "user_access:disable:"
USER_ACCESS_DELETE_PREFIX = "user_access:delete:"
ADMIN_PROMO_VIEW_PREFIX = "admin_promo:view:"
ADMIN_PROMO_TOGGLE_PREFIX = "admin_promo:toggle:"
ADMIN_PROMO_DELETE_PREFIX = "admin_promo:delete:"
ADMIN_PROMO_TYPE_PREFIX = "admin_promo:type:"
ADMIN_PROMO_SCOPE_PREFIX = "admin_promo:scope:"
ADMIN_USER_VIEW_PREFIX = "admin_user:view:"
ADMIN_USER_ISSUE_PREFIX = "admin_user:issue:"
ADMIN_USER_OPEN_ACCESS_PREFIX = "admin_user:open_access:"
ADMIN_USER_HISTORY_PREFIX = "admin_user:history:"
ADMIN_USER_DISABLE_PREFIX = "admin_user:disable:"
ADMIN_USER_REISSUE_PREFIX = "admin_user:reissue:"
ADMIN_ACCESS_ENABLE_PREFIX = "admin_access:enable:"
ADMIN_ACCESS_DISABLE_PREFIX = "admin_access:disable:"
ADMIN_ACCESS_REISSUE_PREFIX = "admin_access:reissue:"
ADMIN_ACCESS_DELETE_PREFIX = "admin_access:delete:"
ADMIN_USERS_BULK_MENU_PREFIX = "admin_users:bulk_menu:"
ADMIN_USERS_GLOBAL_BULK_MENU_PREFIX = "admin_users:global_bulk_menu:"
ADMIN_USERS_BULK_ISSUE_PREFIX = "admin_users:bulk_issue:"
ADMIN_USERS_BULK_ISSUE_CONFIRM_PREFIX = "admin_users:bulk_issue_confirm:"
ADMIN_USERS_GLOBAL_BULK_ISSUE_PREFIX = "admin_users:global_bulk_issue:"
ADMIN_USERS_GLOBAL_BULK_ISSUE_CONFIRM_PREFIX = "admin_users:global_bulk_issue_confirm:"
ADMIN_USERS_BULK_DISABLE_PREFIX = "admin_users:bulk_disable:"
ADMIN_USERS_BULK_DISABLE_CONFIRM_PREFIX = "admin_users:bulk_disable_confirm:"
ADMIN_USERS_GLOBAL_BULK_DISABLE_PREFIX = "admin_users:global_bulk_disable:"
ADMIN_USERS_GLOBAL_BULK_DISABLE_CONFIRM_PREFIX = "admin_users:global_bulk_disable_confirm:"
ADMIN_USERS_BULK_DELETE_PREFIX = "admin_users:bulk_delete:"
ADMIN_USERS_BULK_DELETE_CONFIRM_PREFIX = "admin_users:bulk_delete_confirm:"
ADMIN_USERS_GLOBAL_BULK_DELETE_PREFIX = "admin_users:global_bulk_delete:"
ADMIN_USERS_GLOBAL_BULK_DELETE_CONFIRM_PREFIX = "admin_users:global_bulk_delete_confirm:"
ADMIN_USERS_BULK_OPERATION_REFRESH_PREFIX = "au:op:"
ADMIN_USERS_BULK_OPERATION_CANCEL_PREFIX = "au:x:"
ADMIN_USERS_BULK_OPERATION_ROLLBACK_PREFIX = "au:rb:"
ADMIN_USERS_BULK_HISTORY_PREFIX = "auh:"
ADMIN_USERS_BULK_HISTORY_VIEW_PREFIX = "auhv:"
ADMIN_USERS_PAGE_PREFIX = "admin_users:page:"
ADMIN_USERS_FILTER_PREFIX = "admin_users:filter:"
ADMIN_TICKET_VIEW_PREFIX = "admin_ticket:view:"
ADMIN_TICKET_REPLY_PREFIX = "admin_ticket:reply:"
ADMIN_TICKET_CLOSE_PREFIX = "admin_ticket:close:"
BROADCAST_SEGMENT_PREFIX = "broadcast:segment:"
ACTION_ADMIN_BROADCASTS_CONFIRM = "admin_action:broadcasts_confirm"

SECTION_CALLBACKS = frozenset(
    {
        MENU_BUY,
        MENU_ACCOUNT,
        MENU_REFER,
        MENU_PROMO,
        MENU_STATUS,
        MENU_REVIEWS,
        MENU_SUPPORT,
    }
)

ACTION_CALLBACKS = frozenset(
    {
        ACTION_BUY,
        ACTION_ACCOUNT,
        ACTION_REFER,
        ACTION_PROMO,
        ACTION_STATUS,
        ACTION_REVIEWS,
        ACTION_REVIEW_SKIP,
        ACTION_SUPPORT,
    }
)

ADMIN_SECTION_CALLBACKS = frozenset(
    {
        MENU_ADMIN_HOME,
        MENU_ADMIN_ACCESS,
        MENU_ADMIN_BILLING,
        MENU_ADMIN_USERS,
        MENU_ADMIN_PROMOS,
        MENU_ADMIN_BROADCASTS,
        MENU_ADMIN_SUPPORT,
    }
)

ADMIN_ACTION_CALLBACKS = frozenset(
    {
        ACTION_ADMIN_ACCESS,
        ACTION_ADMIN_BILLING,
        ACTION_ADMIN_USERS,
    }
)

ADMIN_ACCESS_MODE_CALLBACKS = frozenset(
    {
        ACTION_ADMIN_SET_FREE_ACCESS,
        ACTION_ADMIN_SET_BILLING_ENABLED,
        ACTION_ADMIN_SET_MAX_VPN_ACCESSES,
    }
)

ADMIN_USERS_CALLBACKS = frozenset(
    {
        ACTION_ADMIN_USERS_SEARCH,
        ACTION_ADMIN_USERS_REFRESH,
    }
)
