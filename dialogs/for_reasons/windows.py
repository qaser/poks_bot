from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (Back, Button, CurrentPage,
                                        NextPage, PrevPage, Row)
from aiogram_dialog.widgets.text import Const, Format

import utils.constants as texts
from dialogs.for_groups.states import Groups

from . import getters, keyboards, selected

ID_SCROLL_PAGER = 'stations_pager'
STATIONS_TEXT = 'Выберите компрессорную станцию'
GPA_TEXT = 'Выберите номер ГПА'
LINKS_TEXT = 'Перейдите по ссылке чтобы вступить в группу'
EMPTY_TEXT = 'Бот не смог создать ссылки для групп расследования'


async def exit_click(callback, button, dialog_manager):
    try:
        await dialog_manager.done()
        await callback.message.delete()
    except:
        pass


def stations_window():
    return Window(
        Const(STATIONS_TEXT),
        keyboards.paginated_stations(ID_SCROLL_PAGER, selected.on_station_done),
        Row(
            PrevPage(scroll=ID_SCROLL_PAGER, text=Format('<')),
            CurrentPage(scroll=ID_SCROLL_PAGER, text=Format('{current_page1} / {pages}')),
            NextPage(scroll=ID_SCROLL_PAGER, text=Format('>')),
        ),
        Button(Const(texts.EXIT_BUTTON), on_click=exit_click, id='exit'),
        state=Groups.select_station,
        getter=getters.get_stations,
    )


def gpa_window():
    return Window(
        Const(GPA_TEXT),
        keyboards.gpa_btns(selected.on_gpa_done),
        Back(Const(texts.BACK_BUTTON)),
        state=Groups.select_gpa,
        getter=getters.get_gpa,
    )


def links_window():
    return Window(
        Const(LINKS_TEXT, when='not_empty'),
        Const(EMPTY_TEXT, when='empty'),
        keyboards.links_btns(),
        Row(
            PrevPage(scroll='links_pager', text=Format('<')),
            CurrentPage(scroll='links_pager', text=Format('{current_page1} / {pages}')),
            NextPage(scroll='links_pager', text=Format('>')),
            when='is_paginated'
        ),
        Back(Const(texts.BACK_BUTTON)),
        Button(Const(texts.EXIT_BUTTON), on_click=exit_click, id='exit_complete'),
        state=Groups.review_groups,
        getter=getters.get_groups_links,
    )
