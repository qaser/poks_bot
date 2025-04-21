from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (Back, Button, Cancel, CurrentPage,
                                        Group, NextPage, PrevPage, Row, Select)
from aiogram_dialog.widgets.text import Const, Format

import utils.constants as texts
from dialogs.for_edit.states import Edit

from . import getters, keyboards, selected

STATIONS_TEXT = 'Показаны последние 5 групп расследования. Выберите группу для удаления'
FINISH_TEXT = 'Группа удалена'


async def exit_click(callback, button, dialog_manager):
    try:
        await dialog_manager.done()
        await callback.message.delete()
    except:
        pass


def groups_window():
    return Window(
        Const(STATIONS_TEXT),
        keyboards.groups_btns(selected.on_group_done),
        Button(Const(texts.EXIT_BUTTON), on_click=exit_click, id='exit'),
        state=Edit.select_group,
        getter=getters.get_groups,
    )


def confirm_window():
    return Window(
        Format('Вы выбрали:\n\n<b>{group_name}</b>\n'),
        Const('Хотите удалить эту группу?\n\n❗<u>Дейстие необратимо</u>❗'),
        Row(
            Back(Const(texts.BACK_BUTTON)),
            Button(
                Const('✔️ Да'),
                'confirm',
                on_click=selected.on_confirm,
            ),
            id='delete_confirm_btns'
        ),
        state=Edit.delete_confirm,
        getter=getters.get_group_info,
    )


def finish_window():
    return Window(
        Const(FINISH_TEXT),
        Button(Const(texts.EXIT_BUTTON), on_click=exit_click, id='exit_complete'),
        state=Edit.finish_delete,
    )
