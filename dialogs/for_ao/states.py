from aiogram.filters.state import State, StatesGroup


class Ao(StatesGroup):
    select_station = State()
    select_shop = State()
    select_gpa = State()
    select_stats = State()
    ao_confirm = State()
    ao_finish = State()
    select_mode = State()
