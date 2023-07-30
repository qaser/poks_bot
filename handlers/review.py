from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from bson.objectid import ObjectId

from config.bot_config import bot, dp
from config.mongo_config import admins, petitions, buffer, users
from utils.constants import KS
import keyboards.for_review as kb
import utils.constants as const
from utils.decorators import admin_check, registration_check
from aiogram.utils.exceptions import MessageCantBeEdited


# обработка команды /review
# @registration_check
@dp.message_handler(commands=['review'])
async def user_or_admin(message: types.Message):
    if message.chat.type == 'private':
        # await message.delete()
        user_id = message.chat.id
        is_admin = admins.find_one({'user_id': user_id})
        if is_admin is None:
            await user_route(message)
        else:
            await message.delete()
            await choose_direction(message)
    else:
        await message.delete()


async def user_route(message: types.Message):
    user_id = message.chat.id
    ks_users = list(users.find({'user_id': user_id}))
    if len(ks_users) == 1:
        ks = ks_users[0].get('ks')
        await user_choose_direction(message, ks)
    else:
        await message.delete()
        ks_list = [KS.index(i['ks']) for i in ks_users]
        await message.answer(
            text='Выберите компрессорную станцию для просмотра:',
            reply_markup=kb.ks_user_kb(ks_list),
        )


@dp.callback_query_handler(Text(startswith='userks_'))
async def user_choose_ks(call: types.CallbackQuery):
    _, ks_index = call.data.split('_')
    ks = const.KS[int(ks_index)]
    await user_choose_direction(call.message,  ks)


async def user_choose_direction(message: types.Message, ks):
    pipeline = [
        {'$match': {'ks': ks, 'status': {'$in': ['create', 'rework', 'inwork']}}},
        {'$group': {'_id': '$direction', 'count': {'$sum': 1}}},
    ]
    queryset = list(petitions.aggregate(pipeline))
    dir_list = [(i['_id'], i['count']) for i in queryset]
    if len(dir_list) == 0:
        await message.edit_text(
            text='Записи отсутствуют',
        )
    else:
        try:
            await message.edit_text(
                text='Выберите направление для просмотра:',
                reply_markup=kb.user_directions_kb(dir_list, ks),
            )
        except MessageCantBeEdited:
            await message.delete()
            await message.answer(
                text='Выберите направление для просмотра:',
                reply_markup=kb.user_directions_kb(dir_list, ks),
            )


@dp.callback_query_handler(Text(startswith='udir_'))
async def show_user_petitions(call: types.CallbackQuery):
    _, dir_code, ks_id = call.data.split('_')
    msg_ids = []  # для хранения id сообщений, чтобы их потом удалить
    user_id = call.message.chat.id
    ks = const.KS[int(ks_id)]
    dir_name = const.DIRECTIONS_CODES[dir_code]
    qs = list(petitions.find({
        'direction': dir_code,
        'ks': ks,
        'status': {'$in': ['create', 'rework', 'inwork']}
    }))
    len_queryset = len(qs)
    await call.message.delete()
    for pet in qs:
        ks_name = pet.get('ks')
        date = pet.get('date')
        text = pet.get('text')
        pet_id = pet.get('_id')
        status_code = pet.get('status')
        status, _, status_emoji = const.PETITION_STATUS[status_code]
        user_id = pet.get('user_id')
        user = users.find_one({'user_id': user_id})
        username = user.get('username') if user is not None else 'Неизвестен'
        msg = await call.message.answer(
            text=(f'Станция: <b>{ks_name}</b>\n'
                  f'Дата: <b>{date}</b>\n'
                  f'Автор: <b>{username}</b>\n'
                  f'Статус: {status_emoji} <b>{status}</b>\n\n<i>{text}</i>'),
            parse_mode=types.ParseMode.HTML,
            reply_markup=kb.status_kb(pet_id, status_code, 'user')
        )
        msg_ids.append(msg.message_id)
    drop_id = buffer.insert_one({'messages_id': msg_ids}).inserted_id
    summary_text = (
        f'Выше показаны записи ({len_queryset} шт.) <b>{ks_name}</b>.\n'
        f'Направление - "{dir_name}".\n\n'
        '<b>После завершения просмотра нажмите кнопку "Выход"</b>'
    )
    await call.message.answer(
        summary_text,
        reply_markup=kb.get_drop_messages_kb(drop_id),
        parse_mode=types.ParseMode.HTML
    )


async def choose_direction(message: types.Message):
    # await message.delete()
    user_id = message.chat.id
    dirs = admins.find_one({'user_id': user_id}).get('directions', [])
    if len(dirs) != 0:
        pipeline = [
            {'$match': {'status': {'$in': ['create', 'inwork']}, 'direction': {'$in': dirs}}},
            {'$group': {'_id': '$direction', 'count': {'$sum': 1}}},
        ]
        queryset = list(petitions.aggregate(pipeline))
        dir_list = [(i['_id'], i['count']) for i in queryset]
        if len(dir_list) == 0:
            await message.answer(
                text='Записи отсутствуют',
                # reply_markup=kb.directions_kb(dir_list),
            )
        else:
            await message.answer(
                text='Выберите направление для просмотра:',
                reply_markup=kb.directions_kb(dir_list),
            )
    else:
        await message.answer(
            text=('В Вашем профиле нет информации о Вашей специализации. '
                  'Пройдите регистрацию в качестве администратора нажав /admin'),
        )


@dp.callback_query_handler(Text(startswith='dir_'))
async def choose_ks(call: types.CallbackQuery):
    _, dir_code = call.data.split('_')
    qs = list(petitions.find({'direction': dir_code}))
    if len(qs) != 0:
        pipeline = [
            {'$match': {'status': {'$in': ['create', 'inwork']}, 'direction': dir_code}},
            {'$group': {'_id': '$ks', 'count': {'$sum': 1}}},
        ]
        queryset = list(petitions.aggregate(pipeline))
        ks_list = [(i['_id'], KS.index(i['_id']), i['count']) for i in queryset]
        await call.message.edit_text(
            text='Выберите КС:',
            reply_markup=kb.ks_kb(ks_list, dir_code, 'ks'),  # (ks, index_list, count)
        )
    else:
        await call.message.edit_text(
            text='Для данного направления отсутсвуют записи',
            reply_markup=kb.back_kb(dir_code, 'ks')
        )


@dp.callback_query_handler(Text(startswith='ks_'))
async def show_petitions(call: types.CallbackQuery):
    _, ks_index, dir_code = call.data.split('_')
    msg_ids = []  # для хранения id сообщений, чтобы их потом удалить
    ks = const.KS[int(ks_index)]
    dir_name = const.DIRECTIONS_CODES[dir_code]
    queryset = list(petitions.find(
        {'ks': ks, 'direction': dir_code, 'status': {'$in': ['create', 'inwork']}}
    ))
    len_queryset = len(queryset)
    await call.message.delete()
    for pet in queryset:
        ks_name = pet.get('ks')
        date = pet.get('date')
        text = pet.get('text')
        pet_id = pet.get('_id')
        status_code = pet.get('status')
        status, _, status_emoji = const.PETITION_STATUS[status_code]
        user_id = pet.get('user_id')
        user = users.find_one({'user_id': user_id})
        username = user.get('username') if user is not None else 'Неизвестен'
        msg = await call.message.answer(
            text=(f'Станция: <b>{ks_name}</b>\n'
                  f'Дата: <b>{date}</b>\n'
                  f'Автор: <b>{username}</b>\n'
                  f'Статус: {status_emoji} <b>{status}</b>\n\n<i>{text}</i>'),
            parse_mode=types.ParseMode.HTML,
            reply_markup=kb.status_kb(pet_id, status_code, 'admin')
        )
        msg_ids.append(msg.message_id)
    drop_id = buffer.insert_one({'messages_id': msg_ids}).inserted_id
    summary_text = (
        f'Выше показаны записи ({len_queryset} шт.) требующие Вашего внимания.\n'
        f'Направление - "{dir_name}".\n\n'
        '<b>После завершения просмотра нажмите кнопку "Выход"</b>'
    )
    await call.message.answer(
        summary_text,
        reply_markup=kb.get_drop_messages_kb(drop_id),
        parse_mode=types.ParseMode.HTML
    )


@dp.callback_query_handler(Text(startswith='drop_'))
async def drop_messages(call: types.CallbackQuery):
    _, drop_id = call.data.split('_')
    chat_id = call.message.chat.id
    msgs = buffer.find_one({'_id': ObjectId(drop_id)}).get('messages_id')
    for msg_id in msgs:
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    buffer.delete_one({'_id': ObjectId(drop_id)})
    await call.message.delete()


@dp.callback_query_handler(Text(startswith='back_'))
async def menu_back(call: types.CallbackQuery):
    _, level, _ = call.data.split('_')
    if level == 'ks':
        await user_or_admin(call.message)


def register_handlers_review(dp: Dispatcher):
    dp.register_message_handler(
        user_or_admin,
        commands='review'
    )
