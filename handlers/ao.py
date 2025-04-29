import datetime as dt
import re
from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from config.bot_config import bot
from config.mongo_config import emergency_stops, gpa, otkaz_msgs
from config.telegram_config import MY_TELEGRAM_ID, OTKAZ_GROUP_ID
from dialogs.for_ao import windows
from dialogs.for_ao.selected import create_group
from dialogs.for_ao.states import Ao
from handlers.archive import archive_messages
from utils.utils import check_ks

SERVICE_MSG = ('Кто-то ввёл данные в группу "Отказы", '
               'но бот не смог ему отправить сообщение')
BAD_BOT_MSG = 'Бот не смог определить ГПА по сообщению в группе "Отказы"'
GPA_DETECT_TEXT = ('Автоматическое определение ГПА для создания '
                   'группы расследования отказа:')


router = Router()

dialog =  Dialog(
    windows.stations_window(),
    windows.shops_window(),
    windows.gpa_window(),
    windows.stats_choose_window(),
    windows.ao_confirm_window(),
    windows.finish_window(),
)


@router.message(Command('ao'))
async def ao_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    # print(message)
    # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
    await dialog_manager.start(Ao.select_station, mode=StartMode.RESET_STACK)


@router.message(Command('fix'))
async def delete_msgs(message: Message):
    await bot.delete_messages(
        chat_id=OTKAZ_GROUP_ID,
        message_ids=[1432]
    )


@router.message(F.chat.id == -1001856019654)  # для pusha
# @router.message(F.chat.id == -1002275406614 and F.message_thread_id == None)
async def auto_otkaz_detect(message: Message):
    msg_text = escape(message.text)
    otkaz_msgs.insert_one({'msg_id': message.message_id, 'text': msg_text})
    await archive_messages(message)
#     gpa_num_find = re.compile(r'№(\d*)')
#     date_find = re.compile(r'\d\d\.\d\d\.(\d\d\d\d|\d\d)')
#     lpu_find = re.compile(r'\w+ое\sЛПУМГ|\w+-\w+ое\sЛПУМГ')
#     ks_find = re.compile(r'\w+ая|\w+ая')
#     date = date_find.search(message.text)
#     num_gpa = gpa_num_find.search(message.text)
#     lpu = lpu_find.search(message.text)
#     ks = ks_find.search(message.text)
#     try:
#         lpu_name = lpu.group()
#     except AttributeError:
#         lpu_name = None
#     try:
#         ks = f'{ks.group()} КС'
#         ks = check_ks(ks)
#     except AttributeError:
#         ks = None
#     try:
#         day, month, year = date.group().split('.')
#         year = f'20{year}' if len(year) == 2 else year
#         date = f'{day}.{month}.{year}'
#     except AttributeError:
#         date = dt.datetime.now().strftime('%d.%m.%Y')
#     try:
#         num_gpa = num_gpa.group()
#     except AttributeError:
#         num_gpa = None
#     if lpu_name is not None and num_gpa is not None:
#         queryset = list(gpa.find({'lpu': lpu_name, 'num_gpa': num_gpa[1:]}))
#         if len(queryset) > 1 and ks is not None:
#             gpa_instance = gpa.find_one({'lpu': lpu_name, 'num_gpa': num_gpa[1:], 'ks': ks})
#             if gpa_instance is not None:
#                 await prepare_to_create_group(gpa_instance)
#         elif len(queryset) == 1:
#             gpa_instance = queryset[0]
#             await prepare_to_create_group(gpa_instance)
#         else:
#             await bot.send_message(MY_TELEGRAM_ID, f'{BAD_BOT_MSG}\n\n{message.text}')
#     elif ks is not None and num_gpa is not None:
#         gpa_instance = gpa.find_one({'ks': ks, 'num_gpa': num_gpa[1:]})
#         if gpa_instance is not None:
#             await prepare_to_create_group(gpa_instance)
#         else:
#             await bot.send_message(MY_TELEGRAM_ID, f'{BAD_BOT_MSG}\n\n{message.text}')
#     else:
#         await bot.send_message(MY_TELEGRAM_ID, f'{BAD_BOT_MSG}\n\n{message.text}')


# async def prepare_to_create_group(agr):
#     station = agr['ks']
#     gpa_num = agr['num_gpa']
#     date = dt.datetime.today().strftime('%d.%m.%Y')
#     ao_id = emergency_stops.insert_one(
#         {
#             'date': date,
#             'station': station,
#             'gpa': gpa_num,
#             'gpa_id': agr['_id']
#         }
#     ).inserted_id
#     try:
#         await create_group(None, ao_id, 'auto')
#     except:
#         emergency_stops.delete_one({'_id': ao_id})
