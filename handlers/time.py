import re
import datetime as dt

from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram import F, Router
from bson import ObjectId
from config.bot_config import bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from dialogs.for_ao import windows
from dialogs.for_ao.states import Ao
from dialogs.for_ao.selected import create_group
from config.telegram_config import MY_TELEGRAM_ID
from config.mongo_config import gpa, emergency_stops


router = Router()



# @router.message(F.message_thread_id == 216)  # для pusha
@router.message(F.message_thread_id == 19)
async def parse_operating_time(message: Message):
    # gpa_num_find = re.compile(r'№(\d\d|\d\d\d)')
    # date_find = re.compile(r'\d\d\.\d\d\.(\d\d\d\d|\d\d)')
    # lpu_find = re.compile(r'\w+ое\sЛПУМГ|\w+-\w+ое\sЛПУМГ')
    # ks_find = re.compile(r'\w+ая|\w+ая')
    # date = date_find.search(message.text)
    # num_gpa = gpa_num_find.search(message.text)
    # lpu = lpu_find.search(message.text)
    # ks = ks_find.search(message.text)
    print('11111')
