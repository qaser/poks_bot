import datetime as dt

from aiogram_dialog import DialogManager, StartMode

import utils.constants as const
from time import sleep
from config.bot_config import bot
from config.mongo_config import admins, emergency_stops, gpa, groups, users
from config.telegram_config import BOT_ID, MY_TELEGRAM_ID
from config.mail_config import SPCH_REPORT_MAIL
from dialogs.for_iskra.states import Iskra
from dateutil.relativedelta import relativedelta
from utils.create_iskra_report_excel import create_report_excel
from utils.send_email import send_email

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


async def send_report(callback, widget, manager: DialogManager):
    date = dt.datetime.now() - relativedelta(months=1)
    pipeline = [
        {'$lookup': {'from': 'operating_time', 'localField': '_id', 'foreignField': 'gpa_id', 'as': 'working_data'}},
        {'$unwind': '$working_data'},
        {'$match': {'working_data.year': date.year, 'working_data.month': date.month}},
        {'$group': {'_id': '$ks', 'gpa_ids': {'$push': "$_id"}}},
        {'$project': {'_id': 0, 'ks': '$_id', 'gpa_ids': 1}},
        {'$sort': {'ks': 1}}
    ]
    queryset = list(gpa.aggregate(pipeline))
    f_path = create_report_excel(queryset, date)
    sleep(5.0)
    await send_email([SPCH_REPORT_MAIL], f_path, user_id=MY_TELEGRAM_ID)
    await manager.switch_to(Iskra.send_mail_done)


async def on_select_date(callback, widget, manager: DialogManager):
    await manager.switch_to(Iskra.select_year)


async def on_select_year(callback, widget, manager: DialogManager, year):
    context = manager.current_context()
    context.dialog_data.update(year=year)
    await manager.switch_to(Iskra.select_month)


async def on_select_month(callback, widget, manager: DialogManager, month):
    context = manager.current_context()
    context.dialog_data.update(month=month)
    # await manager.switch_to(Iskra.select_month)
