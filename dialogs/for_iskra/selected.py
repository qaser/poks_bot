import datetime as dt

from aiogram_dialog import DialogManager, StartMode

import utils.constants as const
from config.bot_config import bot
from config.mongo_config import admins, emergency_stops, gpa, groups, users
from config.telegram_config import BOT_ID, MY_TELEGRAM_ID
from dialogs.for_iskra.states import Iskra

from . import states


async def on_category(callback, widget, manager: DialogManager):
    await manager.start(states.Iskra.select_category, mode=StartMode.RESET_STACK)


async def on_last_work_time(callback, widget, manager: DialogManager):
    await manager.switch_to(states.Iskra.show_main_report)


async def ks_next(callback, widget, manager: DialogManager):
    context = manager.current_context()
    saved_index = int(context.dialog_data['index_num'])
    index_sum = int(context.dialog_data['index_sum']) - 1
    new_index = saved_index + 1 if saved_index < index_sum else 0
    context.dialog_data.update(index_num=new_index)
    await manager.switch_to(Iskra.show_main_report)


async def ks_prev(callback, widget, manager: DialogManager):
    context = manager.current_context()
    saved_index = int(context.dialog_data['index_num'])
    index_sum = int(context.dialog_data['index_sum']) - 1
    new_index = saved_index - 1 if saved_index > 0 else index_sum
    context.dialog_data.update(index_num=new_index)
    await manager.switch_to(Iskra.show_main_report)
