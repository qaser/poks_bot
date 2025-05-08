from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (Back, Button, CurrentPage, NextPage,
                                        PrevPage, Row)
from aiogram_dialog.widgets.text import Const, Format, Multi

import utils.constants as texts
from config.pyrogram_config import app
from dialogs.custom_widgets.custom_calendar import CustomCalendar
from dialogs.for_request.states import Request

from . import getters, keyboards, selected

ID_SCROLL_PAGER = 'stations_pager'
MAJOR_SCROLL_PAGER = 'majors_pager'
REQUEST_SCROLL_PAGER = 'requests_pager'
KS_SCROLL_PAGER = 'ks_pager'
MAIN_MENU = 'Управление заявками на пуск ГПА.\nВыберите категорию:'
STATIONS_TEXT = 'Выберите компрессорную станцию'
SHOPS_TEXT = 'Выберите номер компрессорного цеха'
GPA_TEXT = 'Выберите номер ГПА'
INPUT_TEXT = 'Введите дополнительную информацию о Вашей заявке в тексте сообщения ниже и нажмите кнопку ➤'
FINISH_TEXT = 'Запрос отправлен на согласование. Вам придёт сообщение с результатом согласования.'
PATHS_EMPTY = 'Правила согласования заявок не установлены. Вы можете установить их кнопками ниже:'
PATH_TUNE = 'Вы настраиваете правила согласования по направлению:'
DATE_TEXT = 'Выберите дату запланированного пуска ГПА'
TIME_TEXT = 'Выберите время запланированного пуска ГПА'


async def exit_click(callback, button, dialog_manager):
    try:
        await dialog_manager.done()
        await callback.message.delete()
    except:
        pass


async def return_main_menu(callback, button, dialog_manager):
    await dialog_manager.switch_to(Request.select_category)


async def return_sorting_menu(callback, button, dialog_manager):
    await dialog_manager.switch_to(Request.select_sorting_requests)


def select_category_window():
    return Window(
        Const(MAIN_MENU),
        keyboards.category_buttons(),
        Button(Const(texts.EXIT_BUTTON), on_click=exit_click, id='exit'),
        state=Request.select_category,
        getter=getters.get_users_info
    )


def stations_window():
    return Window(
        Const(STATIONS_TEXT),
        keyboards.paginated_stations(ID_SCROLL_PAGER, selected.on_station_done),
        Row(
            PrevPage(scroll=ID_SCROLL_PAGER, text=Format('<')),
            CurrentPage(scroll=ID_SCROLL_PAGER, text=Format('{current_page1} / {pages}')),
            NextPage(scroll=ID_SCROLL_PAGER, text=Format('>')),
        ),
        Button(Const(texts.BACK_BUTTON), on_click=return_main_menu, id='main_menu'),
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


def date_window():
    return Window(
        Const(DATE_TEXT),
        CustomCalendar(
            id='calendar',
            on_click=selected.on_select_date,
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=Request.select_date,
    )


def time_window():
    return Window(
        Const(TIME_TEXT),
        keyboards.time_btns(selected.on_select_time),
        Back(Const(texts.BACK_BUTTON)),
        state=Request.select_time,
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
        Format('<u>Вы выбрали:</u>\n{station}\nГПА ст.№ {gpa_num}\n'),
        Format('<u>Срок запуска ГПА:</u>\n{req_date} - {req_time}\n'),
        Format('<u>Текст заявки:</u>\n<i>{request_text}</i>'),
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


def inwork_requests_window():
    return Window(
        Const('Заявки на согласовании', when='not_empty'),
        Const('Заявки на согласовании отсутствуют', when='is_empty'),
        keyboards.paginated_requests(REQUEST_SCROLL_PAGER, selected.on_selected_inwork_request),
        Row(
            PrevPage(scroll=REQUEST_SCROLL_PAGER, text=Format('<')),
            CurrentPage(scroll=REQUEST_SCROLL_PAGER, text=Format('{current_page1} / {pages}')),
            NextPage(scroll=REQUEST_SCROLL_PAGER, text=Format('>')),
            when='not_empty'
        ),
        Button(Const(texts.BACK_BUTTON), on_click=return_main_menu, id='main_menu'),
        state=Request.inwork_requests,
        getter=getters.get_inwork_requests,
    )


def show_inwork_single_request_window():
    return Window(
        Format('{text}'),
        Back(Const(texts.BACK_BUTTON)),
        state=Request.show_inwork_single_request,
        getter=getters.get_single_request,
    )


def select_sorting_requests_window():
    return Window(
        Const('Выберите способ группировки заявок:'),
        keyboards.sort_requests_buttons(),
        Button(Const(texts.BACK_BUTTON), on_click=return_main_menu, id='main_menu'),
        state=Request.select_sorting_requests,
    )


def status_sort_requests_window():
    return Window(
        Const('Выберите требуемый статус заявок:'),
        keyboards.statuses_buttons(selected.on_status_done),
        Button(Const(texts.BACK_BUTTON), on_click=return_sorting_menu, id='sorting_menu'),
        state=Request.status_sort_requests,
        getter=getters.get_statuses,
    )


def ks_sort_requests_window():
    return Window(
        Const(STATIONS_TEXT),
        keyboards.paginated_ks(KS_SCROLL_PAGER, selected.on_ks_done),
        Row(
            PrevPage(scroll=KS_SCROLL_PAGER, text=Format('<')),
            CurrentPage(scroll=KS_SCROLL_PAGER, text=Format('{current_page1} / {pages}')),
            NextPage(scroll=KS_SCROLL_PAGER, text=Format('>')),
        ),
        Button(Const(texts.BACK_BUTTON), on_click=return_sorting_menu, id='sorting_menu'),
        state=Request.ks_sort_requests,
        getter=getters.get_ks,
    )


def date_sort_requests_window():
    return Window(
        Const('Выберите дату, на которую планировался пуск ГПА'),
        CustomCalendar(
            id='calendar',
            on_click=selected.on_date_done,
        ),
        Button(Const(texts.BACK_BUTTON), on_click=return_sorting_menu, id='sorting_menu'),
        state=Request.date_sort_requests,
    )


def show_list_requests_window():
    return Window(
        Format('Заявки со статусом "{status}"', when='is_status'),
        Format('Заявки на компрессоной станции {ks}', when='is_ks'),
        Format('Заявки на {date}', when='is_date'),
        Const('отсутствуют', when='is_empty'),
        keyboards.paginated_requests(REQUEST_SCROLL_PAGER, selected.on_selected_request),
        Row(
            PrevPage(scroll=REQUEST_SCROLL_PAGER, text=Format('<')),
            CurrentPage(scroll=REQUEST_SCROLL_PAGER, text=Format('{current_page1} / {pages}')),
            NextPage(scroll=REQUEST_SCROLL_PAGER, text=Format('>')),
        ),
        Button(
            Const(texts.BACK_BUTTON),
            on_click=selected.on_select_sorting,
            id='sort_status',
            when='is_status'
        ),
        Button(
            Const(texts.BACK_BUTTON),
            on_click=selected.on_select_sorting,
            id='sort_ks',
            when='is_ks'
        ),
        Button(
            Const(texts.BACK_BUTTON),
            on_click=selected.on_select_sorting,
            id='sort_date',
            when='is_date'
        ),
        state=Request.show_list_requests,
        getter=getters.get_requests,
    )


def show_single_request_window():
    return Window(
        Format('{text}'),
        Button(
            Const('🗑️ Удалить заявку'),
            on_click=selected.on_delete_req,
            id='delete_req',
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=Request.show_single_request,
        getter=getters.get_single_request,
    )


def paths_info_window():
    return Window(
        Const(PATHS_EMPTY, when='paths_empty'),
        Const('<u>Правила согласования заявок:</u>\n', when='paths_on'),
        Format('{paths_info}', when='paths_on'),
        keyboards.paths_type_buttons(),
        Button(Const(texts.BACK_BUTTON), on_click=return_main_menu, id='exit'),
        state=Request.paths_info,
        getter=getters.get_paths_info,
    )


def select_num_stage():
    return Window(
        Multi(Const(PATH_TUNE), Format('<u>{path_name}</u>'), sep=' '),
        Const('Выберите количество этапов согласования'),
        keyboards.num_stages_buttons(),
        Back(Const(texts.BACK_BUTTON)),
        state=Request.select_num_stages,
        getter=getters.get_path_name,
    )


def select_majors_window():
    return Window(
        Multi(Const(PATH_TUNE), Format('<u>{path_name}</u>'), sep=' '),
        Format('Количество этапов: <b>{num_stages}</b>\n'),
        Const('Последовательно выберите участников процесса начиная с первого этапа:'),
        Format('{stages_info}'),
        keyboards.paginated_majors(MAJOR_SCROLL_PAGER),
        Row(
            PrevPage(scroll=MAJOR_SCROLL_PAGER, text=Format('<')),
            CurrentPage(scroll=MAJOR_SCROLL_PAGER, text=Format('{current_page1} / {pages}')),
            NextPage(scroll=MAJOR_SCROLL_PAGER, text=Format('>')),
        ),
        Button(
            Const(texts.NEXT_BUTTON),
            id='majors_done',
            on_click=selected.on_majors_done,
            when='complete'
        ),
        Button(
            Const(texts.BACK_BUTTON),
            on_click=selected.back_and_erase_widget_click,
            id='back_with_erase'
        ),
        state=Request.select_majors,
        getter=getters.get_majors_and_stages
    )


def confirm_path_window():
    return Window(
        Const('<u>Проверьте данные перед сохранением:</u>'),
        Format('<b>Наименование:</b> {path_name}'),
        Format('<b>Количество этапов:</b> {num_stages}'),
        Format('{stages_info}'),
        Const('Сохранить?'),
        Row(
            Back(Const(texts.BACK_BUTTON)),
            Button(Const('✔️ Да'), 'path_save', on_click=selected.path_save),
            id='choose_btns'
        ),
        state=Request.path_confirm,
        getter=getters.get_path_complete_info,
    )


def complete_path_window():
    return Window(
        Const('Сохранено'),
        Button(
            Const(texts.EXIT_BUTTON),
            on_click=return_main_menu,
            id='exit'
        ),
        state=Request.path_complete,
    )
