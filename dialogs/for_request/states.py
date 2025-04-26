from aiogram.filters.state import State, StatesGroup


class Request(StatesGroup):
    select_station = State()
    select_shop = State()
    select_gpa = State()
    input_info = State()
    request_confirm = State()
    request_finish = State()
