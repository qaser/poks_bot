import time

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types.message import ContentType
from aiogram.dispatcher.filters import Text

from config.bot_config import bot, dp
from config.mongo_config import archive, groups, users, admins
from config.telegram_config import MY_TELEGRAM_ID
from handlers.emergency_stop import admin_check
import utils.constants as const
from utils.decorators import superuser_check
import keyboards.for_users as kb


# обработка команды /users просмотр пользователей по КС
@admin_check
@dp.message_handler(commands=['users'])
async def users_ks(message: types.Message):
    await show_ks(message)


async def show_ks(message: types.Message):
    pipeline = [
        {'$match': {}},
        {'$group': {'_id': '$ks', 'count': {'$sum': 1}}},
        {'$sort': {'_id': 1}}
    ]
    queryset = list(users.aggregate(pipeline))
    ks_list = [(const.KS.index(i['_id']), i['count']) for i in queryset]
    await message.delete()
    await message.answer(
        text='Выберите станцию для просмотра зарегистрированных пользователей:',
        reply_markup=kb.ks_kb(ks_list)
    )


@dp.callback_query_handler(Text(startswith='users_'))
async def show_users(call: types.CallbackQuery):
    _, ks_index = call.data.split('_')
    ks = const.KS[int(ks_index)]
    qs = list(users.find({'ks': ks}))
    text = ''
    for user in qs:
        prof = const.PROF_USERS[user.get('prof')]
        username = user.get('username')
        text = f'{text}<b>{prof}</b>: {username}\n'
    await call.message.edit_text(
        f'<u>{ks}</u>\n\n{text}',
        reply_markup=kb.back_kb(),
        parse_mode=types.ParseMode.HTML
    )


@dp.callback_query_handler(Text(startswith='users-back'))
async def back_users(call: types.CallbackQuery):
    await show_ks(call.message)


def register_handlers_users(dp: Dispatcher):
    dp.register_message_handler(show_users, commands='users')
