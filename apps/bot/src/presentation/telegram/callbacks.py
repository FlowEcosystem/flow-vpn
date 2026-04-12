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
ACTION_STATUS = "action:status"
ACTION_REVIEWS = "action:reviews"
ACTION_SUPPORT = "action:support"
ACTION_ADMIN_ACCESS = "admin_action:access"
ACTION_ADMIN_BILLING = "admin_action:billing"
ACTION_ADMIN_USERS = "admin_action:users"
ACTION_ADMIN_PROMOS = "admin_action:promos"
ACTION_ADMIN_BROADCASTS = "admin_action:broadcasts"
ACTION_ADMIN_SUPPORT = "admin_action:support"
ACTION_ADMIN_SET_FREE_ACCESS = "admin_action:set_free_access"
ACTION_ADMIN_SET_BILLING_ENABLED = "admin_action:set_billing_enabled"
ACTION_ADMIN_USERS_SEARCH = "admin_action:users_search"
ACTION_ADMIN_USERS_REFRESH = "admin_action:users_refresh"
REVIEW_RATING_PREFIX = "review:rating:"
ADMIN_USER_VIEW_PREFIX = "admin_user:view:"
ADMIN_USER_ISSUE_PREFIX = "admin_user:issue:"
ADMIN_USER_OPEN_ACCESS_PREFIX = "admin_user:open_access:"
ADMIN_USER_HISTORY_PREFIX = "admin_user:history:"
ADMIN_USER_DISABLE_PREFIX = "admin_user:disable:"
ADMIN_USER_REISSUE_PREFIX = "admin_user:reissue:"
ADMIN_USERS_PAGE_PREFIX = "admin_users:page:"
ADMIN_USERS_FILTER_PREFIX = "admin_users:filter:"

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
        ACTION_ADMIN_PROMOS,
        ACTION_ADMIN_BROADCASTS,
        ACTION_ADMIN_SUPPORT,
    }
)

ADMIN_ACCESS_MODE_CALLBACKS = frozenset(
    {
        ACTION_ADMIN_SET_FREE_ACCESS,
        ACTION_ADMIN_SET_BILLING_ENABLED,
    }
)

ADMIN_USERS_CALLBACKS = frozenset(
    {
        ACTION_ADMIN_USERS_SEARCH,
        ACTION_ADMIN_USERS_REFRESH,
    }
)
