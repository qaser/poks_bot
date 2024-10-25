from aiogram import types

import keyboards.for_petition as kb
import utils.constants as const
from config.bot_config import bot
from config.mongo_config import admins, users, docs


def get_creator(user_id):
    if user_id is not None:
        creator_admin = admins.find_one({'user_id': user_id})
        creator_user = users.find_one({'user_id': user_id})
        if creator_admin is None and creator_user is None:
            creator_name = 'Неизвестен'
        elif creator_admin is not None:
            creator_name = creator_admin.get('username')
        elif creator_user is not None:
            creator_name = creator_user.get('username')
        return creator_name
    else:
        return 'Неизвестен'


async def send_petition_to_admins(ks, date, username, msg_text, pet_id, dir):
    pet_docs = docs.find({'pet_id': str(pet_id)})
    num_docs = len(list(pet_docs))if pet_docs is not None else 0
    for adm in list(admins.find({})):
        dirs = adm.get('directions')
        if dir in dirs:
            try:
                await bot.send_message(
                    chat_id=adm.get('user_id'),
                    text=(f'Получена новая запись от <b>{ks}</b>\n'
                          f'Дата: <b>{date.strftime("%d.%m.%Y %H:%M")}</b>\n'
                          f'Автор: <b>{username}</b>\n'
                          f'Статус: {const.CREATE_EMOJI} <b>Создано</b>\n'
                          f'Документы: <b>{num_docs} шт.</b>\n\n{msg_text}'),
                    parse_mode=types.ParseMode.HTML,
                    reply_markup=kb.status_kb(pet_id, 'create', num_docs)
                )
            except:
                continue


def check_ks(ks):  # проверка на наличие буквы ё
    if ks == 'Приозёрная КС':
        return 'Приозерная КС'
    elif ks == 'Таёжная КС':
        return 'Таежная КС'
    return ks
