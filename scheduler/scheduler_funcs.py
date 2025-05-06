import datetime as dt
import imaplib
import os

from aiogram.exceptions import AiogramError
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pytz import timezone

import utils.constants as const
from config.bot_config import bot
from config.mail_config import (ADMIN_EMAIL, IMAP_MAIL_SERVER, MAIL_LOGIN,
                                MAIL_PASS)
from config.mongo_config import groups, msgs, reqs, users, gpa
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
    now_plus_5h = now + dt.timedelta(hours=5)

    res = list(reqs.find({
        'status': 'approved',
        'is_complete': False,
        'notification_datetime': {'$lt': now_plus_5h}
    }))

    message = f"{now.strftime('%d.%m.%Y %H:%M')} - Найдено: {len(res)}\n"

    for doc in res:
        notification_time = doc['notification_datetime']
        # Приводим к одному часовому поясу для корректного сравнения
        if notification_time.tzinfo is None:
            notification_time = notification_time.replace(tzinfo=timezone('UTC'))
        notification_time = notification_time.astimezone(tz)

        time_diff = now_plus_5h - notification_time
        hours_diff = time_diff.total_seconds() / 3600  # Переводим секунды в часы

        message += (f"\nЗаявка {doc['_id']}:\n"
                   f"Плановое время: {notification_time.strftime('%d.%m.%Y %H:%M')}\n"
                   f"Отставание: {hours_diff:.1f} часов\n"
                   f"Текст: {doc.get('text', 'нет текста')}\n")

    await bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text=message
    )
    # for req in res:
    #     prime_date = req['datetime'].astimezone(tz).strftime('%d.%m.%Y %H:%M')
    #     req_date = req['request_datetime'].astimezone(tz).strftime('%d.%m.%Y %H:%M')
    #     gpa_instance = gpa.find_one({'_id': req['gpa_id']})
    #     msg_text=(
    #         f'Ваш запрос от {prime_date} на пуск ГПА №{gpa_instance["num_gpa"]} ({req["ks"]}) '
    #         f'был согласован. Согласованное время запуска {req_date} со временем, отведенным на пуск '
    #         'прошло.\nЕсли запуск ГПА завершён успешно нажмите кнопку "Пуск завершён".\n'
    #         'Если во время запуска возникли проблемы нажмите "Пуск не завершён"'
    #     )
    #     kb = InlineKeyboardBuilder()
    #     kb.button(text='🔴 Пуск не завершён', callback_data=f'launch_fail_{req["_id"]}')
    #     kb.button(text='🟢 Пуск завершён', callback_data=f'launch_success_{req["_id"]}')
    #     kb.adjust(1)
    #     try:
    #         await bot.send_message(
    #             chat_id=req['author_id'],
    #             text=msg_text,
    #             reply_markup=kb.as_markup()
    #         )
    #         await bot.send_message(
    #             chat_id=MY_TELEGRAM_ID,
    #             text='🟢 Отправлено сообщение с кнопками подтверждения пуска'
    #         )
    #     except Exception as err:
    #         await bot.send_message(
    #             chat_id=MY_TELEGRAM_ID,
    #             text='🔴 Не отправлено сообщение с кнопками подтверждения пуска'
    #         )
