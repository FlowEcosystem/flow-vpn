from aiogram.fsm.state import State, StatesGroup


class AdminUsersSearchState(StatesGroup):
    waiting_query = State()


class AdminMaxVpnAccessesState(StatesGroup):
    waiting_value = State()


class AdminPromoCreationState(StatesGroup):
    waiting_code = State()
    waiting_title = State()
    waiting_type = State()
    waiting_bonus_days = State()
    waiting_scope = State()
    waiting_max_redemptions = State()


class AdminSupportReplyState(StatesGroup):
    waiting_reply = State()


class AdminBroadcastCreationState(StatesGroup):
    waiting_text = State()
    waiting_confirm = State()
