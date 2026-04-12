from aiogram.fsm.state import State, StatesGroup


class PromoCodeState(StatesGroup):
    waiting_code = State()


class ReviewState(StatesGroup):
    waiting_text = State()


class SupportState(StatesGroup):
    waiting_message = State()
