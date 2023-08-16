from aiogram import Dispatcher, types
import time

from config.bot_config import bot, dp
from config.mongo_config import admins
from config.telegram_config import MY_TELEGRAM_ID

from utils.create_summary_excel import create_summary_excel
from utils.send_email import send_email


@dp.message_handler(commands=['mail'])
async def mail_handler(message: types.Message):
    create_summary_excel('week')
    time.sleep(5.0)
    queryset = list(admins.find({}))
    emails = [admin.get('mail') for admin in queryset if admin.get('mail') is not None]
    await bot.send_message(chat_id=MY_TELEGRAM_ID, text=emails)
    # await send_email(emails)


def register_handlers_mail(dp: Dispatcher):
    dp.register_message_handler(mail_handler, commands='mail')
