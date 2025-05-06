import asyncio
import logging

from aiogram import F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram_dialog import setup_dialogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import utils

import utils.constants as const
from config.bot_config import bot, dp
from config.mongo_config import admins
from config.pyrogram_config import app
from config.telegram_config import MY_TELEGRAM_ID
from handlers import (administrators, ao, archive, copy, edit, groups, iskra,
                      request, service)
from middlewares.admin_check import AdminCheckMiddleware
from scheduler.scheduler_funcs import (clear_msgs, find_overdue_requests,
                                       send_backups, send_remainder,
                                       send_work_time_reminder)


def get_peer_type_new(peer_id: int) -> str:
    peer_id_str = str(peer_id)
    if not peer_id_str.startswith('-'):
        return 'user'
    elif peer_id_str.startswith('-100'):
        return 'channel'
    else:
        return 'chat'
utils.get_peer_type = get_peer_type_new


@dp.message(Command('reset'))
async def reset_handler(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    await message.answer(
        'Текущее состояние бота сброшено',
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(Command('help'))
async def help_handler(message: Message):
    await message.answer(const.HELP_ADMIN)


@dp.message(Command('admin'))
async def admin_handler(message: Message):
    user = message.from_user
    admins.update_one(
        {'user_id': user.id},
        {'$set': {'directions': ['gpa'], 'username': user.full_name}},
        upsert=True
    )
    await message.answer('Администратор добавлен')
    await bot.send_message(
        MY_TELEGRAM_ID,
        f'Добавлен администратор {user.full_name}'
    )
    await message.delete()


@dp.message(Command('start'))
async def start_handler(message: Message):
    await message.answer(const.INITIAL_TEXT)


# удаление сервисных сообщений
@dp.message(
        F.content_type.in_([
            'pinned_message',
            'left_chat_member',
            'forum_topic_created',
            'forum_topic_closed',
            'forum_topic_edited',
            'forum_topic_reopened',
            'new_chat_members'
        ])
    )
async def delete_service_pinned_message(message: Message):
    try:
        await message.delete()
    except:
        pass


async def main():
    dp.message.middleware(AdminCheckMiddleware())
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_remainder,
        'cron',
        day_of_week='mon-sun',
        hour=18,
        minute=0,
        timezone=const.TIME_ZONE
    )
    scheduler.add_job(
        clear_msgs,
        'cron',
        day_of_week='mon-sun',
        hour=17,
        minute=55,
        timezone=const.TIME_ZONE
    )
    scheduler.add_job(
        send_work_time_reminder,
        'cron',
        day='1',
        hour=8,
        minute=0,
        timezone=const.TIME_ZONE
    )
    scheduler.add_job(
        send_backups,
        'cron',
        day_of_week='mon-sun',
        hour=13,
        minute=30,
        timezone=const.TIME_ZONE
    )
    # задача, которая будет выполняться каждый час
    scheduler.add_job(
        find_overdue_requests,
        'cron',
        minute=40,
        timezone=const.TIME_ZONE
    )
    # scheduler.add_job(
    #     find_overdue_requests,
    #     'cron',
    #     day_of_week='mon-sun',
    #     hour=20,
    #     minute=0,
    #     timezone=const.TIME_ZONE
    # )
    scheduler.start()
    dp.include_routers(
        copy.router,
        service.router,
        iskra.router,
        ao.router,
        groups.router,
        edit.router,
        administrators.router,
        request.router,
        administrators.dialog,
        request.dialog,
        ao.dialog,
        iskra.dialog,
        groups.dialog,
        edit.dialog,
        archive.router,
    )
    setup_dialogs(dp)
    await app.start()
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(
        filename='logs_bot.log',
        level=logging.INFO,
        filemode='a',
        format='%(asctime)s - %(message)s',
        datefmt='%d.%m.%y %H:%M:%S',
        encoding='utf-8',
    )
    asyncio.run(main())
