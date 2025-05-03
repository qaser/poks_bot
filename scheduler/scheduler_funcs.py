import datetime as dt
import imaplib
import os

from aiogram.exceptions import AiogramError
from pytz import timezone

import utils.constants as const
from config.bot_config import bot
from config.mail_config import (ADMIN_EMAIL, IMAP_MAIL_SERVER, MAIL_LOGIN,
                                MAIL_PASS)
from config.mongo_config import groups, msgs, reqs, users
from config.telegram_config import (EXPLOIT_GROUP_ID, MY_TELEGRAM_ID,
                                    SPCH_THREAD_ID)
from utils.backup_db import send_dbs_mail
from utils.get_mail import get_letters

SPCH_TIME_WORK_MSG = ('В срок до 12:00 текущего дня прошу выложить фактическую наработку за прошедший месяц.\n\n'
                      'Пример:\n\nКС «Примерная»:\nГПА 12 - 720\nГПА 24 - 9\n\n'
                      'Соблюдайте форму примера для корректной автоматической обработки данных')


async def clear_msgs():
    queryset = list(msgs.find({}))
    for msg in queryset:
        try:
            await bot.delete_message(chat_id=int(msg['chat_id']), message_id=msg['msg_id'])
        except AiogramError:
            pass
        msgs.delete_one({'chat_id': msg['chat_id'], 'message_id': msg['msg_id']})


async def send_remainder():
    queryset = list(groups.find({'sub_banned': 'false'}))
    num_groups = groups.count_documents({'sub_banned': 'false'})
    await bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text=f'Всего отслеживается групп: {num_groups}'
    )
    count_groups = 0
    for group in queryset:
        id = group.get('_id')
        name = group.get('group_name')
        try:
            msg = await bot.send_message(chat_id=int(id), text=const.GROUP_REMAINDER)
            msgs.insert_one({'msg_id': msg.message_id, 'chat_id': id})
            await bot.send_message(
                chat_id=MY_TELEGRAM_ID,
                text=f'Группе "{name}" отправлено напоминание'
            )
            count_groups = count_groups + 1
        except AiogramError:
            pass
    await bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text=('Задача рассылки уведомлений завершена.\n'
              f'Всего обработано групп: {count_groups}')
    )


async def send_task_users_reminder():
    queryset = users.distinct('user_id')
    for user_id in queryset:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=const.TASK_REMINDER,
            )
        except:
            pass


async def check_mailbox():
    mail_pass = MAIL_PASS
    username = MAIL_LOGIN
    imap_server = IMAP_MAIL_SERVER
    imap = imaplib.IMAP4_SSL(imap_server)
    status, res = imap.login(username, mail_pass)
    if status == 'OK' and imap:
        await get_letters(imap)


async def send_backups():
    cur_date = dt.datetime.now().strftime('%d-%m-%y')
    # backup_dir = f'C:\Dev\poks_bot\\var\\backups\mongobackups\{cur_date}'
    backup_dir = f'../../../var/backups/mongobackups/{cur_date}'
    for db_name in os.listdir(backup_dir):
        if db_name in ['poks_bot_db', 'tehnika_bot_db', 'quiz_db']:
            # backup_path = f'{backup_dir}\{db_name}'
            backup_path = f'{backup_dir}/{db_name}'
            emails = [ADMIN_EMAIL]
            await send_dbs_mail(emails, db_name, backup_path)


async def send_work_time_reminder():
    await bot.send_message(
        chat_id=EXPLOIT_GROUP_ID,
        text=SPCH_TIME_WORK_MSG,
        message_thread_id=SPCH_THREAD_ID
    )


async def find_overdue_requests():
    tz = timezone(const.TIME_ZONE)
    now = dt.datetime.now(tz)
    res = list(reqs.find({
        'status': 'approved',
        'is_complete': False,
        'notification_datetime': {'$lt': now}
    }))
    for req in res:
        date = req['datetime']
        text=f'Ваш запрос от'
        await bot.send_message(
            chat_id=req['author_id'],
            text=''
        )
    print(res)
    # await bot.send_message(
    #     chat_id=MY_TELEGRAM_ID,
    #     text=res
    # )
