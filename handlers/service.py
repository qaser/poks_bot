import time

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types.message import ContentType

from config.bot_config import bot
from config.mongo_config import archive, groups, users, admins
from config.telegram_config import MY_TELEGRAM_ID
from handlers.emergency_stop import admin_check
import utils.constants as const
from utils.decorators import superuser_check


# обработка команды /reset - сброс клавиатуры и состояния
async def reset_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await state.reset_state()
    await message.answer(
        text='Текущее действие отменено',
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await bot.delete_message(message.chat.id, message.message_id)


# обработка команды /users просмотр количества пользователей в БД
@admin_check
async def count_users(message: types.Message):
    queryset = list(users.find({}))
    users_count = len(queryset)
    final_text = ''
    for user in queryset:
        username = '{}, {}'.format(user['_id'], user['username'])
        final_text = '{}\n\n{}'.format(username, final_text)
    await message.answer(
        text=f'Количество пользователей в БД: {users_count}\n\n{final_text}'
    )


# обработка команды /nousers просмотр количества пользователей в БД
@admin_check
async def count_nousers(message: types.Message):
    num_of_stations = len(const.KS)
    queryset = list(users.find({}))
    res = []  # список внесённых станций
    for i in queryset:
        stan = i.get('_id')
        res.append(stan)
    unusers_count = num_of_stations - len(queryset)
    final_text = ''
    for station in const.KS:
        if station not in res:
            final_text = '{}\n{}'.format(final_text, station)
    await message.answer(
        text=f'Станции, с отсутствием данных: {final_text}'
    )
    await message.answer(
        text=f'Осталось {unusers_count}'
    )


# запрет на рассылку уведомлений
@admin_check
async def stop_subscribe(message: types.Message):
    group_id = message.chat.id
    group_check = groups.find_one({'_id': group_id})
    if group_check is not None:
        groups.update_one(
            {'_id': group_id},
            {'$set': {'sub_banned': 'true',}},
            upsert=False
        )
        await message.answer('Напоминания для этой группы отключены')
    else:
        await message.answer(
            'Информации об этой группе не найдено.\n'
            'Удалите бота из группы, а затем снова добавьте'
        )
    await bot.delete_message(message.chat.id, message.message_id)


# включение рассылки уведомлений
@admin_check
async def start_subscribe(message: types.Message):
    group_id = message.chat.id
    group_check = groups.find_one({'_id': group_id})
    if group_check is not None:
        groups.update_one(
            {'_id': group_id},
            {'$set': {'sub_banned': 'false'}},
            upsert=False
        )
        await message.answer('Напоминания для этой группы включены')
    else:
        await message.answer(
            text=('Информации об этой группе не найдено.\n'
                  'Удалите бота из группы, а затем снова добавьте')
        )
    await bot.delete_message(message.chat.id, message.message_id)


# обработка команды /log
@superuser_check
async def send_logs(message: types.Message):
    file = f'logs_bot.log'
    with open(file, 'rb') as f:
        content = f.read()
        await bot.send_document(chat_id=MY_TELEGRAM_ID, document=content)


# @dp.message_handler(commands=['link'])
# async def create_chat_link(message: types.Message):
#     groups_id = list(groups.find({}))
#     links = []
#     supergroup_links = []
#     for i in groups_id:
#         id = i.get('_id')
#         name = i.get('group_name')
#         try:
#             link = await bot.export_chat_invite_link(chat_id=id)
#             links.append((name, link))
#         except exceptions.MigrateToChat:
#             supergroup_links.append((id, exceptions.MigrateToChat.args))
#     for t in links:
#         name, link = t
#         await message.answer(f'{name}\n{link}')
#     for lnk in supergroup_links:
#         await message.answer(lnk)


async def archive_messages(message: types.Message):
    chat = message.chat.id
    if message.photo:
        await bot.send_photo(
            MY_TELEGRAM_ID,
            photo=message.photo[-1].file_id,
            caption=message.chat.full_name
        )
    if message.document:
        await bot.send_document(
            MY_TELEGRAM_ID,
            document=getattr(message, 'document').file_id,
            caption=message.chat.full_name
        )
    if message.text:
        data = archive.find_one({'_id': chat})
        if data is None:
            archive.insert_one({'_id': chat, 'messages': [message.text]})
        else:
            data.get('messages').append(message.text)
            archive.update_one(
                {'_id': chat},
                {'$set': {'messages': data.get('messages')}},
                upsert=False
            )


# обработка команды /check
@admin_check
async def check_admins(message: types.Message):
    await message.delete()
    queryset = list(admins.find({}))
    res_text = ''
    dir_list = []
    for adm in queryset:
        name = adm.get('username')
        directions = adm.get('directions')
        dir_text = ''
        for dir in directions:
            if dir not in dir_list:
                dir_list.append(dir)
            dir_text = f'{dir_text}    {const.DIRECTIONS_CODES[dir]}\n'
        res_text = f'{res_text}\n<b>{name}:</b>\n{dir_text}'
        dirs_not_used = []
        for code, name in const.DIRECTIONS_CODES.items():
            if code not in dir_list:
                dirs_not_used.append(name)
        if len(dirs_not_used) == 0:
            summary = '<u>На все направления назначены специалисты</u>'
        else:
            res = ''
            for i in dirs_not_used:
                res = f'{res}{i}\n'
            summary = f'<u>Направления без отслеживания:</u>\n{res}'
    await message.answer(
        text=f'{res_text}\n{summary}',
        parse_mode=types.ParseMode.HTML
    )


def register_handlers_service(dp: Dispatcher):
    dp.register_message_handler(reset_handler, commands='reset', state='*')
    # dp.register_message_handler(count_users, commands='users')
    # dp.register_message_handler(count_nousers, commands='nousers')
    dp.register_message_handler(stop_subscribe, commands='unsub')
    dp.register_message_handler(start_subscribe, commands='sub')
    dp.register_message_handler(send_logs, commands='log')
    dp.register_message_handler(
        check_admins,
        commands='check',
        chat_type=types.ChatType.PRIVATE
    )
    dp.register_message_handler(archive_messages, content_types=ContentType.ANY)
