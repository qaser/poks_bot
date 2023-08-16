import imaplib
import logging
from time import sleep

from aiogram.utils.exceptions import ChatNotFound, MigrateToChat, Unauthorized
from pymongo.errors import DuplicateKeyError

import utils.constants as const
from config.bot_config import bot
from config.mail_config import IMAP_MAIL_SERVER, MAIL_LOGIN, MAIL_PASS
from config.mongo_config import admins, groups, users
from config.telegram_config import MY_TELEGRAM_ID
from utils.create_summary_excel import create_summary_excel
from utils.get_mail import get_letters
from utils.send_email import send_email


async def send_remainder():
    queryset = list(groups.find({'sub_banned': 'false'}))
    for group in queryset:
        id = group.get('_id')
        try:
            await bot.send_message(chat_id=int(id), text=const.GROUP_REMAINDER)
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
            except (ChatNotFound, Unauthorized):
                groups.delete_one({'_id': err.migrate_to_chat_id})
        except (ChatNotFound, Unauthorized) as err:
            groups.delete_one({'_id': id})


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


async def export_excel_week():
    create_summary_excel('week')


async def export_excel_month():
    create_summary_excel('month')


async def send_mail_summary(period):
    queryset = list(admins.find({}))
    emails = list(set([admin.get('mail') for admin in queryset if admin.get('mail') is not None]))
    create_summary_excel(period)
    sleep(5.0)
    await send_email(['huji@mail.ru', 'dangerexit@gmail.com'], user_id=MY_TELEGRAM_ID)
