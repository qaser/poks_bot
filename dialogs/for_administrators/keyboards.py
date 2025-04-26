from aiogram_dialog.widgets.kbd import Button, Column, ScrollingGroup, Select, Row, Multiselect
from aiogram_dialog.widgets.text import Const, Format

from . import selected


SCROLLING_HEIGHT = 6


def paginated_admins(id_pager, on_click):
    return ScrollingGroup(
        Select(
            Format('{item[username]}'),
            id='s_admins',
            item_id_getter=lambda x: x['user_id'],
            items='admins',
            on_click=on_click,
        ),
        id=id_pager,
        width=1,
        height=SCROLLING_HEIGHT,
        hide_pager=True,
        hide_on_single_page=True
    )


def category_buttons():
    return Column(
        Button(
            Const('📝 Список администраторов'),
            id='admins_list',
            on_click=selected.on_admins_list
        ),
        Button(
            Const('📚 Правила согласования запросов'),
            id='paths',
            on_click=selected.on_paths
        ),
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
