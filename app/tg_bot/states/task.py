from aiogram.fsm.state import State, StatesGroup


class TaskCreation(StatesGroup):
    waiting_for_project = State()
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_deadline = State()
    waiting_for_time_spent = State()
    waiting_for_assignee = State()


class TaskModification(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_deadline = State()
    waiting_for_assignee = State()


class TimeTracking(StatesGroup):
    waiting_for_duration = State()
