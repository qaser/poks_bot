from aiogram.filters.state import State, StatesGroup


class Edit(StatesGroup):
    select_group = State()
    delete_confirm = State()
    finish_delete = State()
