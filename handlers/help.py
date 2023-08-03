from aiogram import types, Dispatcher
from aiogram.utils import executor

from config.bot_config import bot, dp
from scheduler.scheduler_jobs import scheduler, scheduler_jobs
from texts.initial import HELP_ADMIN, HELP_USER
from utils.decorators import registration_check
from config.mongo_config import admins, users


@registration_check
@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    if message.chat.type == 'private':
        user_id = message.from_user.id
        is_admin = admins.find_one({'user_id': user_id})
        is_user = users.find_one({'user_id': user_id})
        if is_admin is not None:
            await bot.send_message(user_id, text=f'{HELP_ADMIN}')
        elif is_user is not None:
            await bot.send_message(user_id, text=f'{HELP_USER}')
        else:
            await bot.send_message(
                user_id,
                ('Вы не зарегистрированы в системе.\n'
                    'Вам не доступна эта команда')
            )
    await message.delete()


def register_handlers_help(dp: Dispatcher):
    dp.register_message_handler(help_handler, commands='help')
