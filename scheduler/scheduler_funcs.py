from config.bot_config import bot
from config.mongo_config import groups
from texts.initial import REMAINDER
from utils.send_email import send_email
from utils.get_mail import get_letters
import imaplib

from config.mail_config import MAIL_LOGIN, MAIL_PASS, IMAP_MAIL_SERVER


async def send_remainder():
    queryset = list(groups.find({'sub_banned': 'false'}))
    for group in queryset:
        id = group.get('_id')
        try:
            await bot.send_message(
                chat_id=int(id),
                text=REMAINDER
            )
        except:
            pass


async def send_report():
    await send_email()


async def check_mailbox():
    mail_pass = MAIL_PASS
    username = MAIL_LOGIN
    imap_server = IMAP_MAIL_SERVER
    imap = imaplib.IMAP4_SSL(imap_server)
    status, res = imap.login(username, mail_pass)
    if status == 'OK' and imap:
        await get_letters(imap)
