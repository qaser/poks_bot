from aiogram_dialog.widgets.kbd import Group, Select
from aiogram_dialog.widgets.text import Format

SCROLLING_HEIGHT = 6


def groups_btns(on_click):
    return Group(
        Select(
            Format('{item[0]}'),
            id='s_groups',
            item_id_getter=lambda x: x[1],
            items='groups',
            on_click=on_click,
        ),
        id='groups_btns',
        width=1,
    )
