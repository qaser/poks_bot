from aiogram.filters.state import State, StatesGroup


class Admins(StatesGroup):
    select_admin = State()
    show_admin = State()
    delete_confirm = State()
