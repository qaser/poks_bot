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
    # категория "Заявки в работе"
    inwork_requests = State()  # с этого состояния перепрыгиваем на select_category
    show_inwork_single_request = State()
    # категория "Архив заявок"
    select_sorting_requests = State()  # с этого состояния перепрыгиваем на select_category
    date_sort_requests = State()
    status_sort_requests = State()
    ks_sort_requests = State()
    show_list_requests = State()  # c этого состояния нужно переходить туда откуда пришел
    show_single_request = State()
    # категория "Настройка"
    paths_info = State()  # с этого состояния перепрыгиваем на select_category
    select_num_stages = State()
    select_majors = State()
    path_confirm = State()
    path_complete = State()
