from aiogram_dialog.widgets.kbd import (Button, Column, Multiselect, Row,
                                        ScrollingGroup, Select)
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
