from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.bot_config import bot, dp
from config.mongo_config import users, admins
from config.telegram_config import MY_TELEGRAM_ID
from utils.constants import KS, PROF_USERS


class Registration(StatesGroup):
    waiting_station = State()
    waiting_prof = State()
    waiting_confirm = State()


# обработка команды /registration
@dp.message_handler(commands=['registration'], chat_type=types.ChatType.PRIVATE)
async def station_choose(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for station in KS:
        keyboard.add(station)
    await message.answer(
        text=(
            'Боту необходимо узнать место Вашей работы.\n'
            'Выберите название компрессорной станции из списка ниже'
        ),
        reply_markup=keyboard
    )
    await message.delete()
    await Registration.waiting_station.set()


async def prof_choose(message: types.Message, state: FSMContext):
    if message.text not in KS:
        await message.answer(
            'Пожалуйста, выберите КС, используя список ниже.'
        )
        return
    await state.update_data(station=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for prof_code, prof_name in PROF_USERS.items():
        keyboard.add(prof_name)
    await message.answer(
        text=(
            'Боту необходимо узнать Вашу должность.\n'
            'Выберите наименование должности из списка ниже'
        ),
        reply_markup=keyboard
    )
    await Registration.waiting_prof.set()


async def confirm(message: types.Message, state: FSMContext):
    if message.text not in PROF_USERS.values():
        await message.answer(
            'Пожалуйста, выберите должность, используя список ниже.'
        )
        return
    await state.update_data(prof=message.text)
    buffer_data = await state.get_data()
    station = buffer_data['station']
    prof = buffer_data['prof']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Нет', 'Да')
    await message.answer(
        text=f'Вы выбрали:\n\n{station}\n{prof}\n\nСохранить?',
        reply_markup=keyboard,
    )
    await Registration.waiting_confirm.set()


async def user_save(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer(
            'Пожалуйста, отправьте "Да" или "Нет"'
        )
        return
    if message.text.lower() == 'да':
        buffer_data = await state.get_data()
        station = buffer_data['station']
        prof = buffer_data['prof']
        for p_code, p_name in PROF_USERS.items():
            if p_name == prof:
                prof_code = p_code
        user = message.from_user
        users.update_one(
            {'user_id': user.id, 'prof': prof_code, 'ks': station},
            {'$set': {'username': user.full_name}},
            upsert=True
        )
        await message.answer(
            'Вы успешно прошли регистрацию',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.finish()
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=f'Пройден процесс регистрации\n\n{prof}: {station}, {user.full_name}'
        )
    else:
        await message.answer(
            ('Данные не сохранены.\n'
             'Если необходимо вновь пройти регистрацию - нажмите /registration'),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.finish()


def register_handlers_registration(dp: Dispatcher):
    dp.register_message_handler(prof_choose, state=Registration.waiting_station)
    dp.register_message_handler(confirm, state=Registration.waiting_prof)
    dp.register_message_handler(user_save, state=Registration.waiting_confirm)
