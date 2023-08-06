import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId
from aiogram.dispatcher import filters

from config.bot_config import bot, dp
from config.mongo_config import admins, users, petitions, buffer
from aiogram.utils.exceptions import CantInitiateConversation
import keyboards.for_petition as kb
import utils.constants as const
from utils.utils import get_creator


class Petition(StatesGroup):
    waiting_petition_text = State()


class EditPetition(StatesGroup):
    waiting_for_text = State()
    waiting_for_confirm = State()


# точка входа командой /task
@dp.message_handler(commands=['task'])
async def check_users(message: types.Message):
    if message.chat.type == 'private':
        user_id = message.chat.id
        queryset = list(users.find({'user_id': user_id}))
        if len(queryset) == 0:
            await message.answer('Вам не доступна эта команда')
        elif len(queryset) == 1:
            await direction_select(message)
        else:
            ks_list = [const.KS.index(u['ks']) for u in list(queryset)]
            await message.answer(
                text='Вы являетесь руководителем нескольких КС, выберите одну из списка:',
                reply_markup=kb.ks_user_kb(ks_list)
            )


@dp.callback_query_handler(filters.Text(startswith='task-ks_'))
async def mark_ks(call: types.CallbackQuery, state: FSMContext):
    _, ks_id = call.data.split('_')
    ks = const.KS[int(ks_id)]
    await state.update_data({'ks': ks, 'many_ks': 'true'})
    await direction_select(call.message)


async def direction_select(message: types.Message):
    await message.answer(
        text='Выберите направление деятельности для решения проблемного вопроса',
        reply_markup=kb.directions_kb(),  # коллбэк с приставкой "pet"
    )
    await message.delete()


@dp.callback_query_handler(filters.Text(startswith='pet_'))
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
    await state.update_data({'dir': dir, 'msg_id': call.message.message_id})
    await Petition.waiting_petition_text.set()


async def ask_confirmation(message: types.Message, state: FSMContext):
    await state.update_data({'text': message.text})
    data = await state.get_data()
    dir = data['dir']
    msg = data['msg_id']
    if 'many_ks' in data.keys():
        ks = data['ks']
        many_ks = data['many_ks']
        msg_id = buffer.insert_one({'text': message.text, 'ks': ks, 'many_ks': many_ks}).inserted_id
    else:
        msg_id = buffer.insert_one({'text': message.text}).inserted_id
    await state.finish()
    await message.answer(
        text=f'Вы ввели следующий запрос:\n\n<i>"{message.text}"</i>\n\nОтправить?',
        reply_markup=kb.send_kb(dir, msg_id),
        parse_mode=types.ParseMode.HTML
    )
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg)
    # await message.delete()


@dp.callback_query_handler(filters.Text(startswith='ask_'))
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
        # date = dt.datetime.now(tz=const.TZINFO).strftime('%d.%m.%Y %H:%M')
        date = dt.datetime.now(tz=const.TZINFO)
        user = users.find_one({'user_id': user_id})
        ks = msg['ks'] if 'many_ks' in msg.keys() else user.get('ks')
        username = user.get('username') if user is not None else 'Неизвестен'
        msg_text = msg.get('text')
        pet_id= petitions.insert_one(
            {
                'date': date,
                'user_id': user_id,
                'text': msg_text,
                'direction': dir,
                'ks': ks,
                'status': 'create',
                'status_creator': user_id,
            }
        ).inserted_id
        for adm in list(admins.find({})):
            dirs = adm.get('directions')
            if dir in dirs:
                try:
                    await bot.send_message(
                        chat_id=adm.get('user_id'),
                        text=(f'Получена новая запись от <b>{ks}</b>\n'
                              f'Дата: <b>{date.strftime("%d.%m.%Y %H:%M")}</b>\n'
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


@dp.callback_query_handler(filters.Text(startswith='status_'))
async def change_status(call: types.CallbackQuery):
    _, pet_id, new_status, current_status = call.data.split('_')
    pet = petitions.find_one({'_id': ObjectId(pet_id)})
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
        warning_text = '<i>Статус этой записи уже был изменен другим специалистом: </i>\n\n'
    else:
        petitions.update_one(
            {'_id': ObjectId(pet_id)},
            {'$set': {'status': new_status, 'status_creator': call.message.chat.id}}
        )
        creator_name = creator_name = get_creator(call.message.chat.id)
        pet = petitions.find_one({'_id': ObjectId(pet_id)})
        status, _, status_emoji = const.PETITION_STATUS[pet.get('status')]
        warning_text = ''
        if call.message.chat.id != user_id:
            try:
                if new_status == 'rework':
                    await bot.send_message(
                        chat_id=user_id,
                        text=(f'Статус Вашей записи изменён специалистом ПОпоЭКС: {creator_name}.\n\n'
                            f'"{msg_text}"\n\nНовый статус: {status_emoji} {status}\n\n'
                            f'Возможно специалисту ПОпоЭКС не понятен Ваш запрос из-за формулировки или Вы ошиблись адресатом.\n'
                            'Вы можете изменить текст или удалить запись в архив, а затем создать новый запрос'),
                            reply_markup=kb.edit_kb(pet_id)
                    )
                elif new_status == 'create':
                    dir = pet.get('direction')
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
                else:
                    await bot.send_message(
                        chat_id=user_id,
                        text=(f'Статус Вашей записи изменён специалистом ПОпоЭКС: {creator_name}.\n\n'
                            f'"{msg_text}"\n\nНовый статус: {status_emoji} {status}')
                    )
            except CantInitiateConversation:
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
                f'Статус: {status_emoji} <b>{status}</b>\n\n{msg_text}'),
            parse_mode=types.ParseMode.HTML,
            # reply_markup=kb.status_kb(pet_id, status_code)
        )


@dp.callback_query_handler(filters.Text(startswith='edit_'))
async def edit_petition(call: types.CallbackQuery, state: FSMContext):
    _, pet_id = call.data.split('_')
    await state.update_data(pet_id=pet_id)
    await call.message.edit_text(
        'Введите новый текст. Если Вы передумали, то на следующем шаге действие можно отменить.'
    )
    await EditPetition.waiting_for_text.set()


async def edit_confirm(message: types.Message, state: FSMContext):
    await state.update_data(new_text=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Нет', 'Да')
    await message.answer(
        text='Вы точно хотите изменить текст записи?',
        reply_markup=keyboard,
    )
    await EditPetition.waiting_for_confirm.set()


async def save_edit_petition(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer(
            'Пожалуйста, отправьте "Да" или "Нет"'
        )
        return
    if message.text.lower() == 'да':
        buffer_data = await state.get_data()
        new_text = buffer_data['new_text']
        pet_id = buffer_data['pet_id']
        petitions.update_one(
            {'_id': ObjectId(pet_id)},
            {'$set': {'text': new_text}}
        )
        await message.answer(
            text='Текст записи изменен',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await message.answer(
            text='Для изменения статуса записи нажмите кнопку "Отправить"',
            reply_markup=kb.edit_send_kb(pet_id)
        )
        await state.finish()
    else:
        await message.answer(
            'Хорошо. Данные о записи не изменены',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.finish()


@dp.callback_query_handler(filters.Text(startswith='cancel'))
async def ask_cancel(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()


def register_handlers_petition(dp: Dispatcher):
    # dp.register_message_handler(
    #     direction_select,
    #     commands='task'
    # )
    dp.register_message_handler(
        ask_confirmation,
        state=Petition.waiting_petition_text
    )
    dp.register_message_handler(
        edit_confirm,
        state=EditPetition.waiting_for_text
    )
    dp.register_message_handler(
        save_edit_petition,
        state=EditPetition.waiting_for_confirm
    )
