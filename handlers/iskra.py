import datetime as dt
import re
from time import sleep

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, ReactionTypeEmoji
from aiogram_dialog import Dialog, DialogManager, StartMode
from dateutil.relativedelta import relativedelta

import utils.constants as const
from config.bot_config import bot
from config.mail_config import SPCH_REPORT_MAIL
from config.mongo_config import gpa, operating_time
from config.telegram_config import MY_TELEGRAM_ID
from dialogs.for_iskra import windows
from dialogs.for_iskra.states import Iskra
from handlers.archive import archive_messages
from utils.create_iskra_report_excel import create_report_excel
from utils.send_email import send_email
from utils.utils import check_ks

router = Router()

dialog =  Dialog(
    windows.category_window(),
    windows.main_report_window(),
    windows.mail_send_window(),
    windows.select_year_window(),
    windows.select_month_window(),
    windows.ks_report_window(),
)


@router.message(Command('iskra'))
async def operating_time_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    await dialog_manager.start(Iskra.select_category, mode=StartMode.RESET_STACK)


@router.message(Command('iskra_mail'))
async def mail_request(message: Message):
    date = dt.datetime.now()
    prev_month = date - relativedelta(months=1)
    pipeline = [
        {'$lookup': {'from': 'operating_time', 'localField': '_id', 'foreignField': 'gpa_id', 'as': 'working_data'}},
        {'$unwind': '$working_data'},
        {'$match': {'working_data.year': prev_month.year, 'working_data.month': prev_month.month}},
        {'$group': {'_id': '$ks', 'gpa_ids': {'$push': "$_id"}}},
        {'$project': {'_id': 0, 'ks': '$_id', 'gpa_ids': 1}},
        {'$sort': {'ks': 1}}
    ]
    queryset = list(gpa.aggregate(pipeline))
    f_path = create_report_excel(queryset, prev_month)
    sleep(5.0)
    await send_email([SPCH_REPORT_MAIL], f_path, user_id=MY_TELEGRAM_ID)



# @router.message(F.chat.id == -1001908010022 and F.message_thread_id == 216)  # для pusha
@router.message(F.chat.id == -1002648938524)
async def parse_operating_data(message: Message):
    await archive_messages(message)
    ks_find = re.compile(r'\w+ая|\w+-\w+ая')
    msg = message.text.replace(u'\xa0', u' ')
    find_gpa = re.findall('ГПА\s*\d+\s*-\s*\d+', msg)
    if len(find_gpa) > 0:
        ks = ks_find.search(msg)
        ks = f'{ks.group()} КС' if ks is not None else ''
        ks = check_ks(ks)
        if ks in const.KS:
            for agr in find_gpa:
                num_gpa, work_time = agr.replace(' ', '').split('-')
                num_gpa = num_gpa[3:]
                gpa_instance = gpa.find_one({'ks': ks, 'num_gpa': str(num_gpa)})
                if gpa_instance is not None:
                    gpa_id = gpa_instance['_id']
                    gpa.update_one({'_id': gpa_id}, {'$set': {'iskra_comp': True}})
                    date = dt.datetime.now()
                    previous_month = date - relativedelta(months=1)
                    print(previous_month)
                    operating_time.update_one(
                        {
                            'gpa_id': gpa_id,
                            'month': previous_month.month,
                            'year': previous_month.year,
                        },
                        {'$set': {
                            'reg_date': date,
                            'work_time': int(work_time),
                        }},
                        upsert=True
                    )
            try:
                await message.react([ReactionTypeEmoji(emoji='👍')])
            except:
                await message.answer(
                    text='Информация о наработке принята',
                    disable_notification=True
                )
        else:
            await message.answer(
                text=('Информация о наработке не принята, вероятно '
                      'грамматическая ошибка в названии КС.\n'
                      'Отправьте новое сообщение с наработкой'),
                disable_notification=True
            )
