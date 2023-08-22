import datetime as dt
import imaplib
import logging
import os
from time import sleep

from aiogram.utils.exceptions import ChatNotFound, MigrateToChat, Unauthorized
from pymongo.errors import DuplicateKeyError

import utils.constants as const
from config.bot_config import bot
from config.mail_config import IMAP_MAIL_SERVER, MAIL_LOGIN, MAIL_PASS, ADMIN_EMAIL
from config.mongo_config import admins, groups, users
from config.telegram_config import MY_TELEGRAM_ID
from utils.create_summary_excel import create_summary_excel
from utils.get_mail import get_letters
from utils.send_email import send_email
from utils.backup_db import send_dbs_mail


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
            await bot.send_message(chat_id=int(id), text=const.GROUP_REMAINDER)
            await bot.send_message(
                chat_id=MY_TELEGRAM_ID,
                text=f'Группе "{name}" отправлено напоминание'
            )
            count_groups = count_groups + 1
        except MigrateToChat as err:
            groups.delete_one({'_id': id})
            try:
                groups.insert_one(
                    {
                        '_id': err.migrate_to_chat_id,
                        'group_name': group.get('group_name'),
                        'sub_banned': 'false',
                    }
                )
            except DuplicateKeyError as e:
                logging.exception(f'Исключение сработало {e}')
                pass
            try:
                await bot.send_message(
                    chat_id=err.migrate_to_chat_id,
                    text=const.GROUP_REMAINDER
                )
                await bot.send_message(
                    chat_id=MY_TELEGRAM_ID,
                    text=f'Группе "{name}" отправлено напоминание'
                )
                count_groups = count_groups + 1
            except (ChatNotFound, Unauthorized):
                groups.delete_one({'_id': err.migrate_to_chat_id})
                await bot.send_message(
                    chat_id=MY_TELEGRAM_ID,
                    text=f'Группа "{name}" удалена или удален бот'
                )
        except (ChatNotFound, Unauthorized) as err:
            groups.delete_one({'_id': id})
            await bot.send_message(
                chat_id=MY_TELEGRAM_ID,
                text=f'Группа "{name}" удалена или удален бот'
            )
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


async def send_mail_summary(period):
    queryset = list(admins.find({}))
    emails = list(set([admin.get('mail') for admin in queryset if admin.get('mail') is not None]))
    create_summary_excel(period)
    sleep(5.0)
    await send_email(emails, user_id=MY_TELEGRAM_ID)


async def send_backups():
    cur_date = dt.datetime.now().strftime('%d-%m-%y')
    backup_dir = f'../../../var/backups/mongobackups/{cur_date}'
    for db_name in os.listdir(backup_dir):
        backup_path = f'{backup_dir}/{db_name}'
        emails = [ADMIN_EMAIL]
        await send_dbs_mail(emails, db_name, backup_path)
