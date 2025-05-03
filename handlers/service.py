import datetime as dt

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message
from pytz import timezone

from config.bot_config import bot
from config.mongo_config import groups
from config.telegram_config import MY_TELEGRAM_ID
from utils import constants as const

router = Router()


# запрет на рассылку уведомлений
@router.message(Command('unsub'))
async def stop_subscribe(message: Message):
    group_id = message.chat.id
    group_check = groups.find_one({'_id': group_id})
    if group_check is not None:
        groups.update_one(
            {'_id': group_id},
            {'$set': {'sub_banned': 'true'}},
            upsert=False
        )
        await message.answer('Напоминания для этой группы отключены')
    await message.delete()


# включение рассылки уведомлений
@router.message(Command('sub'))
async def start_subscribe(message: Message):
    group_id = message.chat.id
    group_check = groups.find_one({'_id': group_id})
    if group_check is not None:
        groups.update_one(
            {'_id': group_id},
            {'$set': {'sub_banned': 'false'}},
            upsert=False
        )
        await message.answer('Напоминания для этой группы включены')
    await message.delete()


@router.message(Command('log'))
async def send_logs(message: Message):
    user_id = message.from_user.id
    if user_id == int(MY_TELEGRAM_ID):
        document = FSInputFile(path=r'logs_bot.log')
        await message.answer_document(document=document)
    await message.delete()


@router.message(Command('time'))
async def check_time_handler(message: Message):
    tz = timezone(const.TIME_ZONE)
    now = dt.datetime.now(tz).strftime('%d.%m.%Y %H:%M')
    server_now = dt.datetime.now().strftime('%d.%m.%Y %H:%M')
    await bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text=f'Время для пользователей - {now}\nВремя сервера - {server_now}'
    )
