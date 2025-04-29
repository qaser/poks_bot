from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (Back, Button, CurrentPage, NextPage,
                                        PrevPage, Row)
from aiogram_dialog.widgets.text import Const, Format

import utils.constants as texts
from config.pyrogram_config import app
from dialogs.for_ao.states import Ao

from . import getters, keyboards, selected

ID_SCROLL_PAGER = 'stations_pager'
STATIONS_TEXT = 'Выберите компрессорную станцию, на которой произошёл отказ'
SHOPS_TEXT = 'Выберите номер компрессорного цеха, на котором произошёл отказ'
GPA_TEXT = 'Выберите номер ГПА'
FINISH_TEXT = 'Группа создана'
STATS_TEXT = 'Данный отказ учитывается в статистике наработки на отказ?'


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


def stats_choose_window():
    return Window(
        Const(STATS_TEXT),
        Row(
            Button(
                Const('❌ Нет'),
                'stats_disable',
                on_click=selected.on_stats_chosen,
            ),
            Button(
                Const('✔️ Да'),
                'stats_enable',
                on_click=selected.on_stats_chosen,
            ),
            id='stats_choose_btns'
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=Ao.select_stats,
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
