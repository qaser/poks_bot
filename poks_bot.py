import logging

from aiogram import types
from aiogram.utils import executor

from config.bot_config import bot, dp
from config.mongo_config import groups
from config.telegram_config import MY_TELEGRAM_ID
from handlers.service import register_handlers_service
from texts.initial import INITIAL_TEXT, NEW_GROUP_TEXT


logging.basicConfig(
    filename='logs_bot.log',
    level=logging.INFO,
    filemode='a',
    format='%(asctime)s - %(message)s',
    datefmt='%d.%m.%y %H:%M:%S',
    encoding='utf-8',
)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer(text=INITIAL_TEXT)


# @dp.message_handler(commands=['help'])
# async def help_handler(message: types.Message):
#     await bot.send_message(
#         message.chat.id,
#         text=f'{message.from_user.full_name}{HELP_TEXT}'
#     )
#     await bot.send_message(message.chat.id, text=FINAL_TEXT)


# обработка события - добавление бота группу
@dp.message_handler(content_types=['new_chat_members'])
async def add_bot_message(message: types.Message):
    bot_obj = await bot.get_me()
    bot_id = bot_obj.id
    for chat_member in message.new_chat_members:
        if chat_member.id == bot_id:
            groups.insert_one(
                {
                    '_id': message.chat.id,
                    'group_name': message.chat.title,
                }
            )
            await bot.send_message(
                chat_id=MY_TELEGRAM_ID,
                text=f'Бот добавлен в новую группу: {message.chat.title}'
            )
            await bot.send_message(
                chat_id=message.chat.id,
                text=NEW_GROUP_TEXT
            )
    await bot.delete_message(message.chat.id, message.message_id)


# удаление сервисного сообщения 'пользователь удалён'
@dp.message_handler(content_types=['left_chat_member'])
async def delete_service_message(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)


if __name__ == '__main__':
    register_handlers_service(dp)
    # executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    executor.start_polling(dp, skip_updates=True)
