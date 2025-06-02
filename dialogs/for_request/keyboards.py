from functools import partial

from aiogram_dialog.widgets.kbd import (Button, Column, Group, Multiselect,
                                        Row, ScrollingGroup, Select)
from aiogram_dialog.widgets.text import Const, Format

from . import selected

SCROLLING_HEIGHT = 6


def category_buttons():
    return Column(
        Button(
            Const('📝 Новая заявка'),
            id='new_request',
            on_click=selected.on_select_category,
            # when='is_user',
        ),
        Button(
            Const('🚀 Заявки на согласовании'),
            id='inwork_requests',
            on_click=selected.on_select_category,
        ),
        Button(
            Const('🗄️ Архив заявок'),
            id='archive_requests',
            on_click=selected.on_select_category,
            when='is_admin',
        ),
        Button(
            Const('📚 Правила согласования заявок'),
            id='paths',
            on_click=selected.on_select_category,
            when='is_admin',
        ),
    )


def type_request_buttons():
    return Column(
        Button(
            Const('✅ C согласованием ПОЭКС'),
            id='with_approval',
            on_click=selected.on_select_type_request,
        ),
        Button(
            Const('⚡ Без согласования ПОЭКС'),
            id='without_approval',
            on_click=selected.on_select_type_request,
        )
    )


def paginated_stations(id_pager, on_click):
    return ScrollingGroup(
        Select(
            Format('{item}'),
            id='s_stations',
            item_id_getter=lambda x: x,
            items='stations',
            on_click=on_click,
        ),
        id=id_pager,
        width=1,
        height=SCROLLING_HEIGHT,
        hide_pager=True,
        hide_on_single_page=True
    )


def shops_btns(on_click):
    return Group(
        Select(
            Format('{item}'),
            id='s_shops',
            item_id_getter=lambda x: x,
            items='shops',
            on_click=on_click,
        ),
        id='shops_btns',
        width=2,
    )


def gpa_btns(on_click):
    return Group(
        Select(
            Format('{item}'),
            id='s_gpa',
            item_id_getter=lambda x: x,
            items='gpa',
            on_click=on_click,
        ),
        id='gpa_btns',
        width=2,
    )


def time_btns(on_click):
    # Генерируем кнопки с временами (8:00 - 14:00)
    times = [f'{hour}:00' for hour in range(8, 15)]
    buttons = []
    for time in times:
        buttons.append(
            Button(
                Const(time),
                id=f"time_{time.replace(':', '')}",
                on_click=partial(on_click, time=time),
                when='with_approval'
            )
        )
    return Group(*buttons, id='time_btns', width=2)


def time_btns_ext(on_click):
    # Генерируем кнопки с временами (00:00 - 23:00)
    times = [f'{hour}:00' for hour in range(0, 24, 2)]
    buttons = []
    for time in times:
        buttons.append(
            Button(
                Const(time),
                id=f"time_{time.replace(':', '')}",
                on_click=partial(on_click, time=time),
                when='without_approval'
            )
        )
    return Group(*buttons, id='time_btns', width=2)


def sort_requests_buttons():
    return Column(
        Button(
            Const('🏷️ По типу ГПА'),
            id='sort_type',
            on_click=selected.on_select_sorting,
        ),
        Button(
            Const('📅 По дате'),
            id='sort_date',
            on_click=selected.on_select_sorting,
        ),
        Button(
            Const('📊 По статусу'),
            id='sort_status',
            on_click=selected.on_select_sorting,
        ),
        Button(
            Const('🏤 По станции'),
            id='sort_ks',
            on_click=selected.on_select_sorting,
        ),
    )


def statuses_buttons(on_click):
    return Group(
        Select(
            Format('{item[1]}'),
            id='s_statuses',
            item_id_getter=lambda x: x[0],
            items='statuses',
            on_click=on_click,
        ),
        id='statuses_btns',
        width=1,
    )


def gpa_types_buttons(on_click):
    return Group(
        Select(
            Format('{item[1]}'),
            id='s_types',
            item_id_getter=lambda x: x[0],
            items='gpa_types',
            on_click=on_click,
        ),
        id='types_btns',
        width=1,
    )


def paginated_ks(id_pager, on_click):
    return ScrollingGroup(
        Select(
            Format('{item}'),
            id='s_ks',
            item_id_getter=lambda x: x,
            items='ks',
            on_click=on_click,
        ),
        id=id_pager,
        width=1,
        height=SCROLLING_HEIGHT,
        hide_pager=True,
        hide_on_single_page=True
    )


def paginated_requests(id_pager, on_click):
    return ScrollingGroup(
        Select(
            Format('{item[name]}'),
            id='s_requests',
            item_id_getter=lambda x: x['id'],
            items='requests',
            on_click=on_click,
        ),
        id=id_pager,
        width=1,
        height=SCROLLING_HEIGHT,
        hide_pager=True,
        hide_on_single_page=True,
        when='not_empty'
    )


def paths_type_buttons():
    return Column(
        Button(
            Const('1️⃣ Стационарные ГПА'),
            id='path_type_1',
            on_click=selected.on_path_selected
        ),
        Button(
            Const('2️⃣ Стационарные ГПА (ГТК-10-4)'),
            id='path_type_2',
            on_click=selected.on_path_selected
        ),
        Button(
            Const('3️⃣ ГПА с авиа. приводом'),
            id='path_type_3',
            on_click=selected.on_path_selected
        ),
        Button(
            Const('4️⃣ ГПА с судовым приводом'),
            id='path_type_4',
            on_click=selected.on_path_selected
        ),
    )


def num_stages_buttons():
    return Row(
        Button(
            Const('1'),
            id='num_stages_1',
            on_click=selected.on_num_stages_selected
        ),
        Button(
            Const('2'),
            id='num_stages_2',
            on_click=selected.on_num_stages_selected
        ),
        Button(
            Const('3'),
            id='num_stages_3',
            on_click=selected.on_num_stages_selected
        ),
        Button(
            Const('4'),
            id='num_stages_4',
            on_click=selected.on_num_stages_selected
        ),
    )


def paginated_majors(id_pager):
    return ScrollingGroup(
        Multiselect(
            Format('🟢 {item[username]}'),
            Format('⚪ {item[username]}'),
            id='s_majors',
            item_id_getter=lambda x: x['user_id'],
            items='majors',
            min_selected=0,
            max_selected=4
        ),
        id=id_pager,
        width=1,
        height=SCROLLING_HEIGHT,
        hide_pager=True,
        hide_on_single_page=True
    )


def files_btns():
    return Column(
        Button(Const("📝 Протокол сдачи защит"), id="protocol", on_click=selected.send_req_files, when="has_protocol"),
        Button(Const("📄 Акт продления МРР"), id="act", on_click=selected.send_req_files, when="has_act"),
        Button(Const("📜 Карта подготовки ГПА к пуску"), id="card", on_click=selected.send_req_files, when="has_card"),
        Button(Const("📋 ЭПБ"), id="epb", on_click=selected.send_req_files, when="has_epb"),
        Button(Const("📑 Эксплуатационный формуляр"), id="logbook", on_click=selected.send_req_files, when="has_logbook"),
        Button(Const("🧾 Приоритеты запуска ГПА"), id="priority", on_click=selected.send_req_files, when="has_priority"),
    )


def priority_btns(on_click):
    buttons = []
    for i in range(1, 4):
        buttons.append(
            Button(
                Const(f'{i}'),
                id=f'{i}',
                on_click=partial(on_click, priority=i)
            )
        )
    return Group(*buttons, id='priority_btns', width=3)


def priority_criteria_btns(on_click):
    buttons = []
    for i in range(1, 12):
        buttons.append(
            Button(
                Const(f'{i}'),
                id=f'{i}',
                on_click=partial(on_click, criteria=i)
            )
        )
    return Group(*buttons, id='criteria_btns', width=3)
