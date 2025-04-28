from aiogram_dialog.widgets.kbd import (Button, Column, Group, Row,
                                        ScrollingGroup, Select, Multiselect)
from aiogram_dialog.widgets.text import Const, Format
from functools import partial

from . import selected

SCROLLING_HEIGHT = 6


def category_buttons():
    return Column(
        Button(
            Const('📝 Новая заявка'),
            id='new_request',
            on_click=selected.on_select_category,
            when='is_admin',
        ),
        # Button(
        #     Const('📋 Мои заявки'),
        #     id='my_requests',
        #     on_click=selected.on_select_category,
        #     when='is_user',
        # ),
        # Button(
        #     Const('🚀 Заявки на согласовании'),
        #     id='inwork_requests',
        #     on_click=selected.on_select_category,
        #     when='is_admin',
        # ),
        Button(
            Const('📚 Правила согласования заявок'),
            id='paths',
            on_click=selected.on_select_category,
            when='is_admin',
        ),
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
            )
        )
    return Group(*buttons, id='time_btns', width=2)


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
