from aiogram.fsm.state import State, StatesGroup


class EmployeeCreation(StatesGroup):
    waiting_for_company = State()
    waiting_for_telegram_id = State()
    waiting_for_display_name = State()
    waiting_for_salary = State()
    waiting_for_admin_status = State()


class EmployeeModification(StatesGroup):
    waiting_for_display_name = State()
    waiting_for_salary = State()
