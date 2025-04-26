from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (Back, Button, CurrentPage,
                                        NextPage, PrevPage, Row)
from aiogram_dialog.widgets.text import Const, Format, Multi

import utils.constants as texts
from dialogs.for_administrators.states import Admins

from . import getters, keyboards, selected

ID_SCROLL_PAGER = 'admins_pager'
MAJOR_SCROLL_PAGER = 'majors_pager'
MAIN_MENU = 'Управление администраторами приложения.\nВыберите категорию:'
ADMINS_TEXT = 'Список администраторов приложения. Для просмотра подробной информации выберите одного из списка'
DELETE_TEXT = 'Администратор удалён'
PATHS_EMPTY = 'Правила согласования запросов не установлены. Вы можете установить их кнопками ниже:'
PATH_TUNE = 'Вы настраиваете правила согласования запросов по направлению:'


async def exit_click(callback, button, dialog_manager):
    try:
        await dialog_manager.done()
        await callback.message.delete()
    except:
        pass


async def return_main_menu(callback, button, dialog_manager):
    await dialog_manager.switch_to(Admins.select_category)


async def return_to_admin_info(callback, button, dialog_manager):
    await dialog_manager.switch_to(Admins.show_admin)


def select_category_window():
    return Window(
        Const(MAIN_MENU),
        keyboards.category_buttons(),
        Button(Const(texts.EXIT_BUTTON), on_click=exit_click, id='exit'),
        state=Admins.select_category,
    )


def select_admins_window():
    return Window(
        Const(ADMINS_TEXT),
        keyboards.paginated_admins(ID_SCROLL_PAGER, selected.on_select_admin),
        Row(
            PrevPage(scroll=ID_SCROLL_PAGER, text=Format('<')),
            CurrentPage(scroll=ID_SCROLL_PAGER, text=Format('{current_page1} / {pages}')),
            NextPage(scroll=ID_SCROLL_PAGER, text=Format('>')),
        ),
        Button(Const(texts.BACK_BUTTON), on_click=return_main_menu, id='exit'),
        state=Admins.select_admin,
        getter=getters.get_admins,
    )


def single_admin_window():
    return Window(
        Const('<u>Информация об администраторе:</u>\n'),
        Format('<b>Имя пользователя:</b> {username}'),
        Format('<b>ID пользователя</b>: {user_id}\n'),
        Const(
            '✔️ <i>Пользователь автоматически добавляется в группу расследования</i>',
            when='sub_on'
        ),
        Const(
            '❌ <i>Пользователь не добавляется в группу расследования</i>',
            when='sub_off'
        ),
        Button(
            Const('⟳ Обновить информацию'),
            on_click=selected.update_admin_info,
            id='update_info',
            when='owner'
        ),
        Button(
            Const('▶ Включить автодобавление в группу'),
            on_click=selected.update_admin_sub,
            id='sub',
            when='sub_off'
        ),
        Button(
            Const('⊘ Выключить автодобавление в группу'),
            on_click=selected.update_admin_sub,
            id='unsub',
            when='sub_on'
        ),
        Button(
            Const('✖ Удалить администратора'),
            on_click=selected.confirm_delete_admin,
            id='delete_admin',
            when='not_owner'
        ),
        Back(Const(texts.BACK_BUTTON)),
        Button(Const(texts.EXIT_BUTTON), on_click=exit_click, id='exit'),
        state=Admins.show_admin,
        getter=getters.get_single_admin,
    )


def confirm_delete_window():
    return Window(
        Format('Вы уверены, что хотите удалить пользователя <b>{username}</b> из списка администраторов?'),
        Row(
            Button(
                Const('❌ Нет'),
                'deny',
                on_click=return_to_admin_info,
            ),
            Button(
                Const('✔️ Да'),
                'apply',
                on_click=selected.delete_admin,
            ),
            id='choose_btns'
        ),
        Back(Const(texts.BACK_BUTTON)),
        state=Admins.delete_confirm,
        getter=getters.get_single_admin,
    )


def paths_info_window():
    return Window(
        Const(PATHS_EMPTY, when='paths_empty'),
        Const('<u>Правила согласования запросов:</u>\n', when='paths_on'),
        Format('{paths_info}', when='paths_on'),
        keyboards.paths_type_buttons(),
        Button(Const(texts.BACK_BUTTON), on_click=return_main_menu, id='exit'),
        state=Admins.paths_info,
        getter=getters.get_paths_info,
    )


def select_num_stage():
    return Window(
        Multi(Const(PATH_TUNE), Format('<u>{path_name}</u>'), sep=' '),
        Const('Выберите количество этапов согласования'),
        keyboards.num_stages_buttons(),
        Back(Const(texts.BACK_BUTTON)),
        state=Admins.select_num_stages,
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
        state=Admins.select_majors,
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
        state=Admins.path_confirm,
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
        state=Admins.path_complete,
    )
