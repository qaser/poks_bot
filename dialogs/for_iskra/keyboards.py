from aiogram_dialog.widgets.kbd import (Button, Column, Group, Radio, Row,
                                        ScrollingGroup, Select)
from aiogram_dialog.widgets.text import Const, Format

from config.mongo_config import admins, emergency_stops, gpa, users

from . import selected

SCROLLING_HEIGHT = 6


def categories():
    return Column(
        Button(
            Const('⏳ Последние данные'),
            'last_time',
            on_click=selected.on_last_work_time
        ),
        Button(
            Const('📅 Выбрать по дате'),
            'choose_date',
            on_click=selected.on_select_date,
        ),
    )


def ks_nav_menu():
    return Row(
        Button(
            Const('⬅️'),
            id='prev',
            on_click=selected.ks_prev
        ),
        Button(
            Format('{index_num}/{index_sum}'),
            id='pager',
        ),
        Button(
            Const('➡️'),
            id='next',
            on_click=selected.ks_next
        ),
        when='nav_is_on'
    )


def years_btns(on_click):
    return Group(
        Select(
            Format('{item}'),
            id='s_years',
            item_id_getter=lambda x: x,
            items='years',
            on_click=on_click,
        ),
        id='years',
        width=2
    )


def months_btns(on_click):
    return Group(
        Select(
            Format('{item}'),
            id='s_months',
            item_id_getter=lambda x: x,
            items='months',
            on_click=on_click,
        ),
        id='months',
        width=2
    )


# def paginated_stations(id_pager, on_click):
#     return ScrollingGroup(
#         Select(
#             Format('{item}'),
#             id='s_stations',
#             item_id_getter=lambda x: x,
#             items='stations',
#             on_click=on_click,
#         ),
#         id=id_pager,
#         width=1,
#         height=SCROLLING_HEIGHT,
#         hide_pager=True,
#         hide_on_single_page=True
#     )


# def shops_btns(on_click):
#     return Group(
#         Select(
#             Format('{item}'),
#             id='s_shops',
#             item_id_getter=lambda x: x,
#             items='shops',
#             on_click=on_click,
#         ),
#         id='shops_btns',
#         width=2,
#     )


# def gpa_btns(on_click):
#     return Group(
#         Select(
#             Format('{item}'),
#             id='s_gpa',
#             item_id_getter=lambda x: x,
#             items='gpa',
#             on_click=on_click,
#         ),
#         id='gpa_btns',
#         width=2,
#     )
