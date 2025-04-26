import datetime as dt

from aiogram_dialog import DialogManager, StartMode

import utils.constants as const
from config.bot_config import bot
from config.mongo_config import emergency_stops, gpa, groups
from config.telegram_config import BOT_ID, MY_TELEGRAM_ID, OTKAZ_GROUP_ID
from dialogs.for_groups.states import Groups


async def on_main_menu(callback, widget, manager: DialogManager):
    await manager.start(Groups.select_station, mode=StartMode.RESET_STACK)


async def on_station_done(callback, widget, manager: DialogManager, station):
    context = manager.current_context()
    context.dialog_data.update(station=station)
    await manager.switch_to(Groups.select_gpa)


async def on_gpa_done(callback, widget, manager: DialogManager, gpa_num):
    context = manager.current_context()
    context.dialog_data.update(gpa=gpa_num)
    await manager.switch_to(Groups.review_groups)
