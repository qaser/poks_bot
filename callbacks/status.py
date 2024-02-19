import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation
from bson.objectid import ObjectId

import keyboards.for_petition as kb
import utils.constants as const
from config.bot_config import bot
from config.mongo_config import docs, petitions, users
from utils.utils import get_creator, send_petition_to_admins


async def change_status(call: types.CallbackQuery):
    _, pet_id, new_status, current_status = call.data.split('_')
    pet = petitions.find_one({'_id': ObjectId(pet_id)})
    pet_docs = docs.find({'pet_id': pet_id})
    num_docs = len(list(pet_docs)) if pet_docs is not None else 0
    msg_text = pet.get('text')
    ks = pet.get('ks')
    date = pet.get('date').strftime('%d.%m.%Y %H:%M')
    user_id = pet.get('user_id')
    user = users.find_one({'user_id': user_id})
    username = user.get('username') if user is not None else 'Неизвестен'
    # проверка на изменение статуса другим пользователем
    if pet.get('status') != current_status:
        status, _, status_emoji = const.PETITION_STATUS[pet.get('status')]
        creator_id = pet.get('status_creator')
        creator_name = get_creator(creator_id)
        warning_text = ('Статус этой записи ранее был изменен '
                        f'другим пользователем: <b>{creator_name}</b>\n\n')
    else:
        creator_id = call.message.chat.id
        creator_name = get_creator(creator_id)
        status_log = pet.get('status_log')
        status_date = dt.datetime.now()
        status_log[new_status] = [creator_id, status_date]
        petitions.update_one(
            {'_id': ObjectId(pet_id)},
            {'$set': {
                'status': new_status,
                'status_creator': call.message.chat.id,
                'status_log': status_log,
            }}
        )
        pet = petitions.find_one({'_id': ObjectId(pet_id)})
        pet_docs = docs.find({'pet_id': pet_id})
        num_docs = len(list(pet_docs)) if pet_docs is not None else 0
        status, _, status_emoji = const.PETITION_STATUS[pet.get('status')]
        warning_text = ''
        if call.message.chat.id != user_id:
            try:
                if new_status == 'rework':
                    await bot.send_message(
                        chat_id=user_id,
                        text=(f'Статус Вашей записи изменён специалистом ПОКС: {creator_name}.\n\n'
                              f'"{msg_text}"\n\nНовый статус: {status_emoji} {status}\n\n'
                              f'Возможно специалисту ПОКС не понятен Ваш запрос '
                              'из-за формулировки или Вы ошиблись адресатом.\n'
                              'Вы можете изменить текст или удалить запись в архив, '
                              'а затем создать новый запрос'),
                        reply_markup=kb.edit_kb(pet_id)
                    )
                elif new_status == 'create':
                    dir = pet.get('direction')
                    await send_petition_to_admins(ks, date, username, msg_text, pet_id, dir)
                else:
                    await bot.send_message(
                        chat_id=user_id,
                        text=(f'Статус Вашей записи изменён специалистом ПОКС: {creator_name}.\n\n'
                              f'"{msg_text}"\n\nНовый статус: {status_emoji} {status}')
                    )
            except (CantInitiateConversation, BotBlocked):
                pass  # тут нужно отправить другому юзеру той же станции
    if new_status == 'create':
        await call.message.edit_text('Отправлено')
    else:
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=(f'{warning_text}Запись от <b>{ks}</b>\n'
                  f'Дата: <b>{date}</b>\n'
                  f'Автор: <b>{username}</b>\n'
                  f'Статус: {status_emoji} <b>{status}</b>\n'
                  f'Документы: <b>{num_docs} шт.</b>\n\n{msg_text}'),
            parse_mode=types.ParseMode.HTML,
        )


def register_callbacks_status(dp: Dispatcher):
    dp.register_callback_query_handler(
        change_status,
        Text(startswith='status')
    )
