# from aiogram_dialog import Window
# from aiogram_dialog.widgets.kbd import (Back, Button, Cancel, CurrentPage,
#                                         Group, NextPage, PrevPage, Row, Select)
# from aiogram_dialog.widgets.text import Const, Format

# import utils.constants as texts
# from config.pyrogram_config import app
# from dialogs.for_iskra.states import Iskra

# from . import getters, keyboards, selected

# ID_SCROLL_PAGER = 'stations_pager'
# STATIONS_TEXT = 'Выберите компрессорную станцию, на которой произошёл отказ'
# SHOPS_TEXT = 'Выберите номер компрессорного цеха, на котором произошёл отказ'
# GPA_TEXT = 'Выберите номер ГПА'
# FINISH_TEXT = 'Группа создана'


# async def exit_click(callback, button, dialog_manager):
#     try:
#         await dialog_manager.done()
#         # await callback.message.delete()
#     except:
#         pass


# def category_window():
#     return Window(
#         Const('Выберите какие данные Вы хотите посмотреть'),
#         keyboards.categories(),
#         Button(Const(texts.EXIT_BUTTON), on_click=exit_click, id='exit'),
#         state=Iskra.select_category,
#     )


# def main_report_window():
#     return Window(
#         Format('Информация о наработке ГПА за {month} {year}г.\n'),
#         Format('<b>{station}</b>'),
#         Format('{work_time}\n'),
#         Format('Суммарная наработка: <b>{sum_time} ч.</b>'),
#         keyboards.ks_nav_menu(),
#         Back(Const(texts.BACK_BUTTON)),
#         state=Iskra.show_main_report,
#         getter=getters.get_last_report,
#     )


# def gpa_window():
#     return Window(
#         Const(GPA_TEXT),
#         keyboards.gpa_btns(selected.on_gpa_done),
#         Back(Const(texts.BACK_BUTTON)),
#         state=Ao.select_gpa,
#         getter=getters.get_gpa,
#     )


# def ao_confirm_window():
#     return Window(
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


# def finish_window():
#     return Window(
#         Const(FINISH_TEXT),
#         Format('{users_info}', when='no_users_info'),
#         Button(Const(texts.EXIT_BUTTON), on_click=exit_click, id='exit_complete'),
#         state=Ao.ao_finish,
#         getter=getters.get_users_info,
#     )


# def choose_mode_window():
#     return Window()
# #         Format('Вы выбрали:\n{station}\nГПА ст.№ {gpa_num}\n'),
# #         Format('Согласно БД это: {gpa_name}'),
# #         Format('Количество зарегистрированных АО (ВНО): {ao_count}', when='ao_not_null'),
# #         Const('\nСоздать группу для проведения расследования отказа ГПА?'),
# #         Row(
# #             Back(Const(texts.BACK_BUTTON)),
# #             Button(
# #                 Const('✔️ Да'),
# #                 'confirm',
# #                 on_click=selected.on_confirm,
# #             ),
# #             id='ao_confirm_btns'
# #         ),
# #         state=Ao.ao_confirm,
# #         getter=getters.get_ao_info,
# #     )
