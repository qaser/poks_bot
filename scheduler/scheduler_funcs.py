import imaplib

import utils.constants as const
from config.bot_config import bot
from config.mail_config import IMAP_MAIL_SERVER, MAIL_LOGIN, MAIL_PASS
from config.mongo_config import groups, users
from utils.create_summary_excel import create_summary_excel
from utils.decorators import run_before
from utils.get_mail import get_letters
from utils.send_email import send_email
from aiogram.utils.exceptions import MigrateToChat


async def send_remainder():
    queryset = list(groups.find({'sub_banned': 'false'}))
    for group in queryset:
        id = group.get('_id')
        try:
            await bot.send_message(
                chat_id=int(id),
                text=const.GROUP_REMAINDER
            )
        except MigrateToChat as err:
            await bot.send_message(
                chat_id=err.migrate_to_chat_id,
                text=const.GROUP_REMAINDER
            )


async def send_task_users_reminder():
    # queryset = list(users.find({}))
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
