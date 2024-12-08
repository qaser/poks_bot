from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Button
from aiogram_dialog.widgets.text import Const, Format, Multi

import utils.constants as texts
from dialogs.for_iskra.states import Iskra

from . import getters, keyboards, selected

ID_SCROLL_PAGER = 'stations_pager'
STATIONS_TEXT = 'Выберите компрессорную станцию, на которой произошёл отказ'
SHOPS_TEXT = 'Выберите номер компрессорного цеха, на котором произошёл отказ'
GPA_TEXT = 'Выберите номер ГПА'
FINISH_TEXT = 'Группа создана'
REPORT_IS_EMPTY = 'Данных за прошедший месяц еще нет, выберите в меню другой период'


async def exit_click(callback, button, dialog_manager):
    try:
        await dialog_manager.done()
        await callback.message.delete()
    except:
        pass


async def return_main_menu(callback, button, dialog_manager):
    await dialog_manager.switch_to(Iskra.select_category)


def category_window():
    return Window(
        Const('Выберите какие данные Вы хотите посмотреть'),
        keyboards.categories(),
        Button(Const(texts.EXIT_BUTTON), on_click=exit_click, id='exit'),
        state=Iskra.select_category,
    )


def main_report_window():
    return Window(
        Const(REPORT_IS_EMPTY, when='report_is_empty'),
        Multi(
            Format('Информация о наработке ГПА за {month} {year}г.\n'),
            Format('<b>{ks}</b>'),
            Format('{report_text}\n'),
            Format('Суммарная наработка по КС: <b>{sum_time} ч.</b>'),
            sep='\n',
            when='report_not_empty'
        ),
        keyboards.ks_nav_menu(),
        Button(
            Const('Отправить по email'),
            on_click=selected.send_report,
            id='report_email',
            when='report_not_empty'
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=Iskra.show_main_report,
        getter=getters.get_last_report,
    )


def mail_send_window():
    return Window(
        Const('Письмо отправлено'),
        Back(Const(texts.BACK_BUTTON)),
        state=Iskra.send_mail_done
    )


def select_year_window():
    return Window(
        Const('Выберите год'),
        keyboards.years_btns(selected.on_select_year),
        Button(Const(texts.BACK_BUTTON), on_click=return_main_menu, id='main_menu'),
        getter=getters.get_years,
        state=Iskra.select_year,
    )


def select_month_window():
    return Window(
        Const('Выберите месяц'),
        keyboards.months_btns(selected.on_select_month),
        Back(Const(texts.BACK_BUTTON)),
        getter=getters.get_months,
        state=Iskra.select_month,
    )


def ks_report_window():
    return Window(
        Multi(
            Format('Информация о наработке ГПА за {month} {year}г.\n'),
            Format('<b>{ks}</b>'),
            Format('{report_text}\n'),
            Format('Суммарная наработка по КС: <b>{sum_time} ч.</b>'),
            sep='\n',
        ),
        keyboards.custom_ks_nav_menu(),
        Back(Const(texts.BACK_BUTTON)),
        state=Iskra.show_ks_report,
        getter=getters.get_ks_report,
    )
