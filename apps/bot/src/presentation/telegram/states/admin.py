from aiogram.fsm.state import State, StatesGroup


class AdminUsersSearchState(StatesGroup):
    waiting_query = State()
