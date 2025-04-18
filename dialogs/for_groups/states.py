from aiogram.filters.state import State, StatesGroup


class Groups(StatesGroup):
    select_station = State()
    select_gpa = State()
    review_groups = State()
