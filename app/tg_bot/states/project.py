from aiogram.fsm.state import State, StatesGroup


class ProjectCreation(StatesGroup):
    waiting_for_company = State()
    waiting_for_name = State()
    waiting_for_code = State()
