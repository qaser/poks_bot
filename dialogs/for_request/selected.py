import datetime as dt
import re
import asyncio

from aiogram_dialog import DialogManager, StartMode
from pyrogram.types import ChatPermissions, ChatPrivileges

import utils.constants as const
from config.bot_config import bot
from config.mongo_config import (admins, emergency_stops, gpa, groups,
                                 otkaz_msgs, requests, paths)
from config.pyrogram_config import app
from config.telegram_config import BOT_ID, MY_TELEGRAM_ID, OTKAZ_GROUP_ID
from dialogs.for_request.states import Request


async def on_main_menu(callback, widget, manager: DialogManager):
    await manager.start(Request.select_station, mode=StartMode.RESET_STACK)


async def on_station_done(callback, widget, manager: DialogManager, station):
    context = manager.current_context()
    context.dialog_data.update(station=station)
    await manager.switch_to(Request.select_shop)


async def on_shop_done(callback, widget, manager: DialogManager, shop):
    context = manager.current_context()
    context.dialog_data.update(shop=shop)
    await manager.switch_to(Request.select_gpa)


async def on_gpa_done(callback, widget, manager: DialogManager, gpa_num):
    context = manager.current_context()
    context.dialog_data.update(gpa=gpa_num)
    await manager.switch_to(Request.input_info)


async def on_input_info(callback, widget, manager: DialogManager, request_text):
    context = manager.current_context()
    context.dialog_data.update(request_text=request_text)
    await manager.switch_to(Request.request_confirm)


async def on_confirm(callback, widget, manager: DialogManager):
    author_id = manager.event.from_user.id
    context = manager.current_context()
    num_gpa = context.dialog_data['gpa']
    station = context.dialog_data['station']
    gpa_instance = gpa.find_one({'ks': station, 'num_gpa': num_gpa})
    gpa_id = gpa_instance['_id']
    request_text = context.dialog_data['request_text']
    path_type = get_path_type(gpa_instance)
    path_instance = paths.find_one({'path_type': path_type})
    requests.insert_one(
        {
            'author': author_id,
            'ks': station,
            'gpa_id': gpa_id,
            'datetime': dt.datetime.now(),
            'text': request_text,
            'path_id': path_instance['_id'],
            'current_stage': 1,
            'stages': {}
        }
    )
    #  нужно сделать отправку запроса по пути
    await manager.switch_to(Request.request_finish)


def get_path_type(gpa_instance):
    type_gpa = gpa_instance['type_gpa']
    group_gpa = gpa_instance['group_gpa']
    if type_gpa == 'Стационарные' and group_gpa == 'ГТК-10-4':
        path_type = 'Стационарные ГПА (ГТК-10-4)'
    elif type_gpa == 'Стационарные':
        path_type = 'Стационарные ГПА'
    elif type_gpa == 'Авиационный привод':
        path_type = 'ГПА с авиа. приводом'
    elif type_gpa == 'Судовой привод':
        path_type = 'ГПА с судовым приводом'
    return path_type
