from aiogram import F, Router
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config.bot_config import bot
from config.telegram_config import MY_TELEGRAM_ID
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config.bot_config import bot, dp
from config.mongo_config import users
from utils.constants import KS, PROF_USERS


router = Router()

class Registration(StatesGroup):
    waiting_station = State()
    waiting_prof = State()
    waiting_confirm = State()


# обработка команды /registration
@router.message(Command('registration'))
async def station_choose(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        keyboard = ReplyKeyboardBuilder()
        for station in KS:
            keyboard.button(text=station)
        keyboard.adjust(1)
        await message.answer(
            text=('Боту необходимо узнать место Вашей работы.\n'
                  'Выберите название компрессорной станции из списка ниже'),
            reply_markup=keyboard.as_markup(resize_keyboard=True),
        )
        await message.delete()
        await state.set_state(Registration.waiting_station)
    else:
        await message.delete()


@router.message(Registration.waiting_station)
async def prof_choose(message: types.Message, state: FSMContext):
    if message.text not in KS:
        await message.answer(
            'Пожалуйста, выберите КС, используя список ниже.'
        )
        return
    await state.update_data(station=message.text)
    keyboard = ReplyKeyboardBuilder()
    for prof_code, prof_name in PROF_USERS.items():
        keyboard.button(text=prof_name)
    keyboard.adjust(1)
    await message.answer(
        text=('Боту необходимо узнать Вашу должность.\n'
              'Выберите наименование должности из списка ниже'),
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )
    await state.set_state(Registration.waiting_prof)


@router.message(Registration.waiting_prof)
async def confirm(message: types.Message, state: FSMContext):
    if message.text not in PROF_USERS.values():
        await message.answer('Пожалуйста, выберите должность, используя список ниже.')
        return
    await state.update_data(prof=message.text)
    buffer_data = await state.get_data()
    station = buffer_data['station']
    prof = buffer_data['prof']
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='Нет')
    keyboard.button(text='Да')
    await message.answer(
        text=f'Вы выбрали:\n\n{station}\n{prof}\n\nСохранить?',
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )
    await state.set_state(Registration.waiting_confirm)


@router.message(Registration.waiting_confirm)
async def user_save(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer('Пожалуйста, отправьте "Да" или "Нет"')
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
            {'prof': prof_code, 'ks': station},
            {'$set': {'username': user.full_name, 'user_id': user.id}},
            upsert=True
        )
        await message.answer(
            'Вы успешно прошли регистрацию',
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=f'Пройден процесс регистрации\n\n{prof}: {station}, {user.full_name}'
        )
    else:
        await message.answer(
            ('Данные не сохранены.\n'
             'Если необходимо вновь пройти регистрацию - нажмите /registration'),
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
