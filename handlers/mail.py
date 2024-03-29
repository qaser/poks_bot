import time

from aiogram import Dispatcher, types

from config.bot_config import bot, dp
from config.mongo_config import admins
from handlers.emergency_stop import admin_check
from utils.create_summary_excel import create_summary_excel
from utils.send_email import send_email


@admin_check
@dp.message_handler(commands=['mail'])
async def mail_handler(message: types.Message):
    if message.chat.type == 'private':
        user_id = message.chat.id
        admin = admins.find_one({'user_id': user_id})
        email = admin.get('mail')
        if email is not None:
            create_summary_excel('month')
            msg = await message.answer('Запрос получен, ожидайте')
            time.sleep(5.0)
            await send_email(emails=[email], user_id=admin.get('user_id'))
            try:
                await bot.delete_message(chat_id=user_id, message_id=msg.message_id)
            except:
                pass
        else:
            await message.answer('Информации о Вашем адресе email не найдено')
    await message.delete()


def register_handlers_mail(dp: Dispatcher):
    dp.register_message_handler(mail_handler, commands='mail')
