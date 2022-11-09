import logging

from aiogram import types
from aiogram.utils import executor

from config.bot_config import bot, dp
from config.mongo_config import groups
from config.telegram_config import MY_TELEGRAM_ID
from handlers.emergency_stop import register_handlers_emergency
from handlers.service import register_handlers_service
from scheduler.scheduler_jobs import scheduler, scheduler_jobs
from texts.initial import HELP_TEXT, INITIAL_TEXT, NEW_GROUP_TEXT

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


@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    await bot.send_message(
        message.chat.id,
        text=f'{HELP_TEXT}'
    )


# обработка события - добавление бота в группу
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
                    'sub_banned': 'false',
                }
            )
            await bot.send_message(
                chat_id=MY_TELEGRAM_ID,
                text=f'Бот добавлен в новую группу: {message.chat.title}'
            )
            # отправка приветственного сообщения
            post = await bot.send_message(
                chat_id=message.chat.id,
                text=NEW_GROUP_TEXT
            )
            posts.insert_one({ 'post_id': post.message_id })
    # удаление сервисного сообщения 'добавлен пользователь'
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        pass



# удаление сервисного сообщения 'пользователь удалён'
@dp.message_handler(content_types=['left_chat_member'])
async def delete_bot_message(message: types.Message):
    bot_obj = await bot.get_me()
    bot_id = bot_obj.id
    for chat_member in message.left_chat_member:
        if chat_member.id == bot_id:
            try:
                groups.delete_one({'_id': message.chat.id,})
                await bot.send_message(
                    chat_id=MY_TELEGRAM_ID,
                    text=f'Бот удалён из группы: {message.chat.title}'
                )
            except:
                await bot.send_message(
                    chat_id=MY_TELEGRAM_ID,
                    text=f'Бот удалён из группы, но этой группы нет в БД: {message.chat.title}'
                )
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        pass


# удаление сервисного сообщения 'пользователь удалён'
@dp.message_handler(content_types=['pinned_message'])
async def delete_service_pinned_message(message: types.Message):
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        pass


async def on_startup(_):
    scheduler_jobs()


if __name__ == '__main__':
    scheduler.start()
    register_handlers_service(dp)
    register_handlers_emergency(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
