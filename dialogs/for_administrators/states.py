from aiogram.filters.state import State, StatesGroup


class Admins(StatesGroup):
    select_category = State()
    select_admin = State()
    show_admin = State()
    delete_confirm = State()
    paths_info = State()  # с этого состояния перепрыгиваем на select_category
    select_num_stages = State()
    select_majors = State()
    path_confirm = State()
    path_complete = State()
