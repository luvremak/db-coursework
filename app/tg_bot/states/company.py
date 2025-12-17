from aiogram.fsm.state import State, StatesGroup


class CompanyCreation(StatesGroup):
    waiting_for_name = State()
    waiting_for_code = State()
