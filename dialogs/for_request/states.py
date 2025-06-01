from aiogram.filters.state import State, StatesGroup


class Request(StatesGroup):
    select_category = State()
    # выбор типа запроса (с согласованием ПОЭКС или по распоряжению ДС)
    select_type_request = State()
    show_reject_info = State()

    # первая категория "Новая заявка"
    select_station = State()
    select_shop = State()
    select_gpa = State()

    select_epb = State()
    input_epb_file = State()

    select_date = State()
    select_time = State()

    # опрос о соответствии ГПА требованиям
    select_resource = State()
    input_logbook_file = State()
    select_resource_act = State()
    input_resource_act_file = State()  # каждый 2-ой запрос

    input_out_of_resource_reason = State()

    select_protocol = State()
    input_protocol_file = State()   # каждый 4-ой запрос

    select_card = State()
    input_card_file = State()  # каждый 6-ой запрос

    input_info = State()  # с этого состояния перепрыгиваем на select_category

    select_priority_gpa=State()
    select_priority_criteria=State()
    input_priority_file=State()

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
    type_sort_requests = State()
    show_list_requests = State()  # c этого состояния нужно переходить туда откуда пришел
    show_single_request = State()
    confirm_delete_request = State()

    # категория "Настройка"
    paths_info = State()  # с этого состояния перепрыгиваем на select_category
    select_num_stages = State()
    select_majors = State()
    path_confirm = State()
    path_complete = State()
