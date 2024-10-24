from aiogram_dialog.widgets.kbd import (Button, Column, Group, Select,
                                        Radio, Row, ScrollingGroup)
from aiogram_dialog.widgets.text import Const, Format

from config.mongo_config import emergency_stops, users, admins, gpa

from . import selected

SCROLLING_HEIGHT = 6


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
