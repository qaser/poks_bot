from aiogram_dialog.widgets.kbd import (Group, ListGroup, ScrollingGroup,
                                        Select, Url)
from aiogram_dialog.widgets.text import Format

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


def links_btns():
    return ScrollingGroup(
        ListGroup(
            Url(Format('{item[0]}'), Format('{item[1]}')),
            id='s_links',
            item_id_getter=lambda x: x[1],
            items='links',
        ),
        id='links_pager',
        width=1,
        height=SCROLLING_HEIGHT,
        hide_pager=True,
        # hide_on_single_page=True,
    )
