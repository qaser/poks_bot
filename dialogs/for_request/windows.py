from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (Back, Button, CurrentPage,
                                        NextPage, PrevPage, Row)
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput

import utils.constants as texts
from config.pyrogram_config import app
from dialogs.for_request.states import Request

from . import getters, keyboards, selected

ID_SCROLL_PAGER = 'stations_pager'
STATIONS_TEXT = 'Выберите компрессорную станцию'
SHOPS_TEXT = 'Выберите номер компрессорного цеха'
GPA_TEXT = 'Выберите номер ГПА'
INPUT_TEXT = 'Введите дополнительную информацию о Вашем запросе в тексте сообщения ниже и нажмите кнопку ➤'
FINISH_TEXT = 'Запрос отправлен на согласование'


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
        state=Request.select_station,
        getter=getters.get_stations,
    )


def shops_window():
    return Window(
        Const(SHOPS_TEXT),
        keyboards.shops_btns(selected.on_shop_done),
        Back(Const(texts.BACK_BUTTON)),
        state=Request.select_shop,
        getter=getters.get_shops,
    )


def gpa_window():
    return Window(
        Const(GPA_TEXT),
        keyboards.gpa_btns(selected.on_gpa_done),
        Back(Const(texts.BACK_BUTTON)),
        state=Request.select_gpa,
        getter=getters.get_gpa,
    )


def input_info_window():
    return Window(
        Const(INPUT_TEXT),
        Back(Const(texts.BACK_BUTTON)),
        TextInput(
            id='request_info',
            on_success=selected.on_input_info,
        ),
        state=Request.input_info,
    )


def request_confirm_window():
    return Window(
        Format('<u>Вы выбрали:</u>\n{station}\nГПА ст.№ {gpa_num}'),
        Format('<u>Текст запроса:</u>\n<i>"{request_text}"</i>'),
        Const('\nОтправить запрос на согласование?'),
        Row(
            Back(Const(texts.BACK_BUTTON)),
            Button(
                Const('✔️ Да'),
                'confirm',
                on_click=selected.on_confirm,
            ),
            id='ao_confirm_btns'
        ),
        state=Request.request_confirm,
        getter=getters.get_request_info,
    )


def finish_window():
    return Window(
        Const(FINISH_TEXT),
        Button(Const(texts.EXIT_BUTTON), on_click=exit_click, id='exit_complete'),
        state=Request.request_finish,
    )
