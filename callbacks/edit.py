from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId

import keyboards.for_petition as kb
from config.mongo_config import petitions


class EditPetition(StatesGroup):
    waiting_for_text = State()
    waiting_for_confirm = State()


# @dp.callback_query_handler(Text(startswith='edit_'))
async def edit_petition(call: types.CallbackQuery, state: FSMContext):
    _, pet_id = call.data.split('_')
    await state.update_data(pet_id=pet_id)
    await call.message.edit_text(
        text=('Введите новый текст. Если Вы передумали, '
              'то на следующем шаге действие можно отменить.')
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


def register_callbacks_edit(dp: Dispatcher):
    dp.register_callback_query_handler(
        edit_petition,
        Text(startswith='edit'),
        state=EditPetition.waiting_for_text
    )
    dp.register_message_handler(
        edit_confirm,
        state=EditPetition.waiting_for_text
    )
    dp.register_message_handler(
        save_edit_petition,
        state=EditPetition.waiting_for_confirm
    )
