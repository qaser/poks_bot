import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.message import ContentType
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation
from bson.objectid import ObjectId

import keyboards.for_petition as kb
import utils.constants as const
from config.bot_config import bot
from config.mongo_config import admins, docs, petitions, users


class QuickAnswer(StatesGroup):
    waiting_for_text = State()
    waiting_for_choose = State()
    waiting_for_file = State()


async def quick_answer(call: types.CallbackQuery, state: FSMContext):
    # нужно проверить на наличие ответа от другого специалиста
    _, pet_id = call.data.split('_')
    await state.update_data({'pet_id': pet_id, 'user_id': call.message.chat.id})
    pet_text = petitions.find_one({'_id': ObjectId(pet_id)}).get('text')
    await call.message.edit_text(text=f'Текст запроса:\n\n "{pet_text}"')
    await call.message.answer('Введите Ваш ответ')
    await QuickAnswer.waiting_for_text.set()


async def doc_choose(message: types.Message, state: FSMContext):
    await state.update_data(answer_text=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Отправить без файла')
    keyboard.add('Загрузить файл')
    await message.answer(
        text='Нужно ли прикрепить к сообщению файл?',
        reply_markup=keyboard,
    )
    await QuickAnswer.waiting_for_choose.set()


async def answer_file_upload(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отправить без файла':
        await send_quick_answer(message, state)
    elif message.text.lower() == 'загрузить файл':
        await message.answer(
            text=('Отправьте фото, видео или документ формата .pdf\n\n'
                  'На данный момент можно отправить только один файл'),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await QuickAnswer.waiting_for_file.set()


async def answer_file_save(message: types.Message, state: FSMContext):
    pet_data = await state.get_data()
    num_docs = pet_data.get('num_docs', 0)
    if num_docs < 1:
        pet_id = pet_data.get('pet_id')
        if message.photo:
            file, file_type = message.photo[-1], 'photo'
        elif message.video:
            file, file_type = message.video, 'video'
        elif message.document:
            if message.document.mime_type == 'application/pdf':
                file, file_type = message.document, 'document'
            else:
                await message.answer('Отправьте пожалуйста документ формата .pdf')
                return
        else:
            await message.answer(
                text=('Данные не загружены. Отправьте пожалуйста фото, '
                      'видео или документ формата .pdf')
            )
            return
        docs.insert_one({'pet_id': pet_id, 'file_id': file.file_id, 'file_type': file_type})
        await message.answer('Файл получен')
        num_docs += 1
        await state.update_data(num_docs=num_docs)
        await send_quick_answer(message, state)


async def send_quick_answer(message, state):
    buffer_data = await state.get_data()
    answer_text = buffer_data['answer_text']
    pet_id = buffer_data['pet_id']
    user_id = buffer_data['user_id']
    date = dt.datetime.now(tz=const.TZINFO)
    answers = petitions.find_one({'_id': ObjectId(pet_id)}).get('conversation')
    send_to = answers[-1][1]  # последний кортеж в списке ответов и второй элемент
    answers.append((date, user_id, answer_text))
    petitions.update_one(
        {'_id': ObjectId(pet_id)},
        {'$set': {'conversation': answers}}
    )
    author = admins.find_one({'user_id': message.chat.id})
    is_admin = True
    if author is None:
        author = users.find_one({'user_id': message.chat.id})
        is_admin = False
    author_name = author.get('username')
    try:
        await bot.send_message(
            chat_id=send_to,
            text=f'На Ваш вопрос получен ответ от: {author_name}\n\n{answer_text}',
            reply_markup=kb.answer_kb(pet_id)
        )
    except (CantInitiateConversation, BotBlocked):
        pass
    pet_docs = docs.find({'pet_id': pet_id})
    if pet_docs is not None:
        num_docs = len(list(pet_docs))
        for doc in pet_docs:
            file_id = doc.get('file_id')
            file_type = doc.get('file_type')
            if file_type == 'photo':
                await bot.send_photo(chat_id=send_to, photo=file_id)
            elif file_type == 'video':
                await bot.send_video(chat_id=send_to, video=file_id)
            elif file_type == 'document':
                await bot.send_document(chat_id=send_to, document=file_id)
    await message.answer(
        text='Сообщение отправлено',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.finish()
    await message.answer('Теперь можете изменить статус записи')
    pet = petitions.find_one({'_id': ObjectId(pet_id)})
    ks = pet.get('ks')
    date = pet.get('date').strftime('%d.%m.%Y %H:%M')
    user_id = pet.get('user_id')
    text = pet.get('text')
    user = users.find_one({'user_id': user_id})
    username = user.get('username') if user is not None else 'Неизвестен'
    status_code = pet.get('status')
    status, _, status_emoji = const.PETITION_STATUS[status_code]
    await message.answer(
        text=(f'Запись от <b>{ks}</b>\n'
              f'Дата: <b>{date}</b>\n'
              f'Автор: <b>{username}</b>\n'
              f'Статус: {status_emoji} <b>{status}</b>\n'
              f'Документы: <b>{num_docs} шт.</b>\n\n{text}'),
        parse_mode=types.ParseMode.HTML,
        reply_markup=kb.full_status_kb(pet_id, status_code, num_docs, is_admin)
    )


def register_callbacks_answer(dp: Dispatcher):
    dp.register_callback_query_handler(
        quick_answer,
        Text(startswith='answer'),
    )
    dp.register_message_handler(
        doc_choose,
        state=QuickAnswer.waiting_for_text
    )
    dp.register_message_handler(
        answer_file_upload,
        state=QuickAnswer.waiting_for_choose
    )
    dp.register_message_handler(
        answer_file_save,
        state=QuickAnswer.waiting_for_file,
        content_types=ContentType.ANY
    )
