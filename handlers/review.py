from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from bson.objectid import ObjectId

from config.bot_config import bot, dp
from config.mongo_config import admins, petitions, buffer, users
from utils.constants import KS
import keyboards.for_review as kb
import utils.constants as const
from utils.decorators import admin_check


# обработка команды /review
@admin_check
async def choose_direction(message: types.Message):
    await message.delete()
    user_id = message.chat.id
    dirs = admins.find_one({'user_id': user_id}).get('directions', [])
    if len(dirs) != 0:
        if 'without' in dirs:
            dirs = const.DIRECTIONS_CODES.keys()
        await message.answer(
            text='Выберите направление для просмотра:',
            reply_markup=kb.directions_kb(dirs),
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
        username = users.find_one({'user_id': user_id}).get('username')
        msg = await call.message.answer(
            text=(f'Станция: <b>{ks_name}</b>\n'
                  f'Дата: <b>{date}</b>\n'
                  f'Автор: <b>{username}</b>\n'
                  f'Статус: {status_emoji} <b>{status}</b>\n\n<i>{text}</i>'),
            parse_mode=types.ParseMode.HTML,
            reply_markup=kb.status_kb(pet_id, status_code)
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
        await choose_direction(call.message)


def register_handlers_review(dp: Dispatcher):
    dp.register_message_handler(
        choose_direction,
        commands='review',
        chat_type=types.ChatType.PRIVATE
    )
