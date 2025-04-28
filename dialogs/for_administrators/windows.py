from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (Back, Button, CurrentPage,
                                        NextPage, PrevPage, Row)
from aiogram_dialog.widgets.text import Const, Format

import utils.constants as texts
from dialogs.for_administrators.states import Admins

from . import getters, keyboards, selected

ID_SCROLL_PAGER = 'admins_pager'
ADMINS_TEXT = 'Список администраторов приложения. Для просмотра подробной информации выберите одного из списка'
DELETE_TEXT = 'Администратор удалён'



async def exit_click(callback, button, dialog_manager):
    try:
        await dialog_manager.done()
        await callback.message.delete()
    except:
        pass


async def return_to_admin_info(callback, button, dialog_manager):
    await dialog_manager.switch_to(Admins.show_admin)


def select_admins_window():
    return Window(
        Const(ADMINS_TEXT),
        keyboards.paginated_admins(ID_SCROLL_PAGER, selected.on_select_admin),
        Row(
            PrevPage(scroll=ID_SCROLL_PAGER, text=Format('<')),
            CurrentPage(scroll=ID_SCROLL_PAGER, text=Format('{current_page1} / {pages}')),
            NextPage(scroll=ID_SCROLL_PAGER, text=Format('>')),
        ),
        Button(Const(texts.EXIT_BUTTON), on_click=exit_click, id='exit'),
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
