from aiogram.filters.state import State, StatesGroup


class Reasons(StatesGroup):
    select_type_failure = State()
    select_type_equipment = State()
    select = State()
