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
from config.pyrogram_config import app
from handlers import admin, ao, archive, copy, iskra, registration, service
from scheduler.scheduler_funcs import (clear_msgs, send_backups, send_remainder,
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
    await message.answer(const.HELP_USER)


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
    # scheduler.add_job(
    #     send_mail_summary,
    #     'cron',
    #     day_of_week='mon',
    #     hour=8,
    #     minute=30,
    #     timezone=const.TIME_ZONE,
    #     args=['week']
    # )
    # scheduler.add_job(
    #     send_mail_summary,
    #     'cron',
    #     day=1,
    #     hour=8,
    #     minute=31,
    #     timezone=const.TIME_ZONE,
    #     args=['month']
    # )
    # scheduler.add_job(
    #     send_task_users_reminder,
    #     'cron',
    #     day_of_week='wed',
    #     hour=10,
    #     minute=15,
    #     timezone=const.TIME_ZONE
    # )
    scheduler.add_job(
        send_backups,
        'cron',
        day_of_week='mon-sun',
        hour=13,
        minute=30,
        timezone=const.TIME_ZONE
    )
    scheduler.start()
    dp.include_routers(
        service.router,
        ao.router,
        copy.router,
        admin.router,
        iskra.router,
        registration.router,
        ao.dialog,
        iskra.dialog,
        archive.router
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
