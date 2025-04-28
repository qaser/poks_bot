from aiogram.filters.state import State, StatesGroup


class Request(StatesGroup):
    select_category = State()
    # первая категория "Новая заявка"
    select_station = State()
    select_shop = State()
    select_gpa = State()
    select_date = State()
    select_time = State()
    input_info = State()
    request_confirm = State()
    request_finish = State()
    # категория "Посмотреть заявки"
    show_requests = State()  # с этого состояния перепрыгиваем на select_category
    # категория "Заявки в работе"
    inwork_requests = State()  # с этого состояния перепрыгиваем на select_category
    # категория "Настройка"
    paths_info = State()  # с этого состояния перепрыгиваем на select_category
    select_num_stages = State()
    select_majors = State()
    path_confirm = State()
    path_complete = State()
