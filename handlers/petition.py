import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId

from config.bot_config import bot, dp
from config.mongo_config import admins, users, petitions, buffer
from utils.constants import KS
from aiogram.utils.exceptions import CantInitiateConversation
import keyboards.for_petition as kb
import utils.constants as const
from utils.send_email import send_email


class Petition(StatesGroup):
    waiting_petition_text = State()


# точка входа командой /task
async def direction_select(message: types.Message):
    await message.answer(
        text='Выберите направление деятельности для решения проблемного вопроса',
        reply_markup=kb.directions_kb(),  # коллбэк с приставкой "pet"
    )
    await message.delete()


@dp.callback_query_handler(Text(startswith='pet_'))
async def ask_problem(call: types.CallbackQuery, state: FSMContext):
    _, dir = call.data.split('_')
    dir_name = const.DIRECTIONS_CODES.get(dir)
    await call.message.edit_text(
        text=(
            f'Вы выбрали направление <b>"{dir_name}"</b>\n\n'
            'Введите текст Вашего запроса/предложения/проблемы.\n\n'
            'Сообщение будет отправлено специалисту по выбранному Вами направлению.'
            # 'Если Вы передумали, то нажмите кнопку <b>Отмена</b>'
        ),
        # reply_markup=kb.cancel_kb(),
        parse_mode=types.ParseMode.HTML
    )

    await state.set_data({'dir': dir, 'msg_id': call.message.message_id})
    await Petition.waiting_petition_text.set()


async def ask_confirmation(message: types.Message, state: FSMContext):
    await state.update_data({'text': message.text})
    data = await state.get_data()
    dir = data['dir']
    msg = data['msg_id']
    msg_id = buffer.insert_one({'text': message.text}).inserted_id
    await state.finish()
    await message.answer(
        text=f'Вы ввели следующий запрос:\n\n<i>"{message.text}"</i>\n\nОтправить?',
        reply_markup=kb.send_kb(dir, msg_id),
        parse_mode=types.ParseMode.HTML
    )
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg)
    # await message.delete()


@dp.callback_query_handler(Text(startswith='ask_'))
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
        date = dt.datetime.now(tz=const.TZINFO).strftime('%d.%m.%Y %H:%M')
        user = users.find_one({'user_id': user_id})
        ks = user.get('ks')
        username = user.get('username')
        msg_text = msg.get('text')
        pet_id= petitions.insert_one(
            {
                'date': date,
                'user_id': user_id,
                'text': msg_text,
                'direction': dir,
                'ks': ks,
                'status': 'create'
            }
        ).inserted_id
        for adm in list(admins.find({})):
            dirs = adm.get('directions')
            if dir in dirs:
                try:
                    await bot.send_message(
                        chat_id=adm.get('user_id'),
                        text=(f'Получена новая запись от <b>{ks}</b>\n'
                              f'Дата: <b>{date}</b>\n'
                              f'Автор: <b>{username}</b>\n'
                              f'Статус: {const.CREATE_EMOJI} <b>Создано</b>\n\n{msg_text}'),
                        parse_mode=types.ParseMode.HTML,
                        reply_markup=kb.status_kb(pet_id, 'create')
                    )
                except CantInitiateConversation:
                    continue
        await call.message.edit_text(
            text=(
                f'Ваш запрос отправлен специалисту по направлению <b>"{dir_name}"</b>\n'
                'Чтобы сделать новый запрос нажмите /task'
            ),
            parse_mode=types.ParseMode.HTML,
        )
    buffer.delete_one({'_id': ObjectId(msg_id)})
    await state.finish()


@dp.callback_query_handler(Text(startswith='status_'))
async def change_status(call: types.CallbackQuery):
    _, pet_id, new_status, current_status = call.data.split('_')
    pet = petitions.find_one({'_id': ObjectId(pet_id)})
    msg_text = pet.get('text')
    ks = pet.get('ks')
    date = pet.get('date')
    user_id = pet.get('user_id')
    username = users.find_one({'user_id': user_id}).get('username')
    # проверка на изменение статуса другим пользователем
    if pet.get('status') != current_status:
        status, status_code, status_emoji = const.PETITION_STATUS[pet.get('status')]
        warning_text = '<i>Статус этой записи уже был изменен другим специалистом</i>\n\n'
    else:
        petitions.update_one(
            {'_id': ObjectId(pet_id)},
            {'$set': {'status': new_status}}
        )
        pet = petitions.find_one({'_id': ObjectId(pet_id)})
        status, status_code, status_emoji = const.PETITION_STATUS[pet.get('status')]
        warning_text = ''
        try:
            await bot.send_message(
                chat_id=user_id,
                text=(f'Статус Вашей записи изменён.\n\n'
                    f'"{msg_text}"\n\nНовый статус: {status_emoji} {status}'),
            )
        except CantInitiateConversation:
            pass
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=(f'{warning_text}Запись от <b>{ks}</b>\n'
              f'Дата: <b>{date}</b>\n'
              f'Автор: <b>{username}</b>\n'
              f'Статус: {status_emoji} <b>{status}</b>\n\n{msg_text}'),
        parse_mode=types.ParseMode.HTML,
        # reply_markup=kb.status_kb(pet_id, status_code)
    )


@dp.callback_query_handler(Text(startswith='cancel'))
async def ask_cancel(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()


def register_handlers_petition(dp: Dispatcher):
    dp.register_message_handler(
        direction_select,
        commands='task',
        chat_type=types.ChatType.PRIVATE
    )
    dp.register_message_handler(
        ask_confirmation,
        state=Petition.waiting_petition_text
    )
