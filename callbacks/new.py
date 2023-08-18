import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from bson.objectid import ObjectId

import utils.constants as const
from config.mongo_config import buffer, docs, petitions, users
from utils.utils import send_petition_to_admins


async def save_petition(call: types.CallbackQuery, state: FSMContext):
    _, action, dir, msg_id = call.data.split('_')
    msg = buffer.find_one({'_id': ObjectId(msg_id)})
    if action == 'cancel':
        await call.message.edit_text(
            text='Действие отменено.\nЧтобы сделать новый запрос нажмите /task'
        )
    else:
        dir_name = const.DIRECTIONS_CODES.get(dir)
        user_id = call.message.chat.id
        date = dt.datetime.now(tz=const.TZINFO)
        user = users.find_one({'user_id': user_id})
        ks = msg['ks'] if 'many_ks' in msg.keys() else user.get('ks')
        username = user.get('username') if user is not None else 'Неизвестен'
        msg_text = msg.get('text')
        pet_id = petitions.insert_one(
            {
                'date': date,
                'user_id': user_id,
                'text': msg_text,
                'direction': dir,
                'ks': ks,
                'status': 'create',
                'status_creator': user_id,
                'status_log': {'create': [user_id, date]},
                'conversation': [(date, user_id, msg_text)]
            }
        ).inserted_id
        data = await state.get_data()
        docs_list = data.get('docs')
        if docs_list is not None:
            for doc in docs_list:
                file_id, file_type = doc
                docs.insert_one({'pet_id': str(pet_id), 'file_id': file_id, 'file_type': file_type})
        buffer.delete_one({'_id': ObjectId(msg_id)})
        await state.finish()
        await send_petition_to_admins(ks, date, username, msg_text, pet_id, dir)
        await call.message.edit_text(
            text=(
                f'Ваш запрос отправлен специалисту по направлению <b>"{dir_name}"</b>\n'
                'Чтобы сделать новый запрос нажмите /task'
            ),
            parse_mode=types.ParseMode.HTML,
        )


def register_callbacks_new(dp: Dispatcher):
    dp.register_callback_query_handler(
        save_petition,
        Text(startswith='new'),
        state='*'
    )
