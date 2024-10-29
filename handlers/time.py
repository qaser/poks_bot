import re
import datetime as dt

from dateutil.relativedelta import relativedelta

from aiogram import F, Router
from config.bot_config import bot
from aiogram.types import Message

from config.telegram_config import MY_TELEGRAM_ID
from config.mongo_config import gpa, оperating_time
from utils.utils import check_ks
import utils.constants as const


router = Router()


@router.message(F.chat.id == -1001908010022 and F.message_thread_id == 216)  # для pusha
# @router.message(F.chat.id == -1002345179040 and F.message_thread_id == 3)
async def parse_operating_time(message: Message):
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
                    оperating_time.update_one(
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
            await message.answer(
                text='Информация о наработке принята',
                disable_notification=True
            )
        else:
            await message.answer(
                text=('Информация о наработке не принята, вероятно '
                      'грамматическая ошибка в названии КС'),
                disable_notification=True
            )
