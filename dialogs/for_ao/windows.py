from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (Back, Button, Cancel, CurrentPage,
                                        Group, NextPage, PrevPage, Row, Select)
from aiogram_dialog.widgets.text import Const, Format
from config.pyrogram_config import app

import utils.constants as texts

from . import getters, keyboards, selected
from dialogs.for_ao.states import Ao

ID_SCROLL_PAGER = 'stations_pager'
STATIONS_TEXT = 'Выберите компрессорную станцию, на которой произошёл отказ'
SHOPS_TEXT = 'Выберите номер компрессорного цеха, на котором произошёл отказ'
GPA_TEXT = 'Выберите номер ГПА'
FINISH_TEXT = 'Группа создана'


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
        state=Ao.select_station,
        getter=getters.get_stations,
    )


def shops_window():
    return Window(
        Const(SHOPS_TEXT),
        keyboards.shops_btns(selected.on_shop_done),
        Back(Const(texts.BACK_BUTTON)),
        state=Ao.select_shop,
        getter=getters.get_shops,
    )


def gpa_window():
    return Window(
        Const(GPA_TEXT),
        keyboards.gpa_btns(selected.on_gpa_done),
        Back(Const(texts.BACK_BUTTON)),
        state=Ao.select_gpa,
        getter=getters.get_gpa,
    )


def ao_confirm_window():
    return Window(
        Format('Вы выбрали:\n{station}\nГПА ст.№ {gpa_num}\n'),
        Format('Согласно БД это: {gpa_name}'),
        Format('Количество зарегистрированных АО (ВНО): {ao_count}', when='ao_not_null'),
        Const('\nСоздать группу для проведения расследования отказа ГПА?'),
        Row(
            Back(Const(texts.BACK_BUTTON)),
            Button(
                Const('✔️ Да'),
                'confirm',
                on_click=selected.on_confirm,
            ),
            id='ao_confirm_btns'
        ),
        state=Ao.ao_confirm,
        getter=getters.get_ao_info,
    )


def finish_window():
    return Window(
        Const(FINISH_TEXT),
        Format('{users_info}', when='no_users_info'),
        Button(Const(texts.EXIT_BUTTON), on_click=exit_click, id='exit_complete'),
        state=Ao.ao_finish,
        getter=getters.get_users_info,
    )


def choose_mode_window():
    return Window()
#         Format('Вы выбрали:\n{station}\nГПА ст.№ {gpa_num}\n'),
#         Format('Согласно БД это: {gpa_name}'),
#         Format('Количество зарегистрированных АО (ВНО): {ao_count}', when='ao_not_null'),
#         Const('\nСоздать группу для проведения расследования отказа ГПА?'),
#         Row(
#             Back(Const(texts.BACK_BUTTON)),
#             Button(
#                 Const('✔️ Да'),
#                 'confirm',
#                 on_click=selected.on_confirm,
#             ),
#             id='ao_confirm_btns'
#         ),
#         state=Ao.ao_confirm,
#         getter=getters.get_ao_info,
#     )
