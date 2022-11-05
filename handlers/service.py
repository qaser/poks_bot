import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.bot_config import bot
from config.mongo_config import users
from config.telegram_config import MY_TELEGRAM_ID
from utils.constants import KS
# from texts.initial import SERVICE_END_TEXT, SERVICE_TEXT


class GksManager(StatesGroup):
    waiting_station_name = State()
    waiting_station_confirm = State()


# обработка команды /reset - сброс клавиатуры и состояния
async def reset_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        text='Сброс настроек бота выполнен, текущее действие отменено.',
        reply_markup=types.ReplyKeyboardRemove(),
    )


# обработка команды /users просмотр количества пользователей в БД
async def count_users(message: types.Message):
    queryset = list(users.find({}))
    users_count = len(queryset)
    final_text = ''
    for user in queryset:
        username = '{}, {}'.format(user['_id'], user['username'])
        final_text = '{}\n\n{}'.format(username, final_text)
    await message.answer(
        text=f'Количество пользователей в БД: {users_count}\n\n{final_text}'
    )


# обработка команды /gks - сбор данных о начальниках ГКС
async def station_choose(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for station in KS:
        keyboard.add(station)
    await message.answer(
        text=(
            'Этот опрос только для начальников ГКС (в том числе и врио)\n'
            'Боту необходимо узнать место Вашей работы.\n'
            'Выберите название компрессорной станции из списка ниже'
        ),
        reply_markup=keyboard
    )
    await GksManager.waiting_station_name.set()


async def station_confirm(message: types.Message, state: FSMContext):
    await state.update_data(station=message.text)
    buffer_data = await state.get_data()
    station = buffer_data['station']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Нет', 'Да')
    await message.answer(
        text=f'Вы выбрали {station}. Сохранить?',
        reply_markup=keyboard,
    )
    await GksManager.waiting_station_confirm.set()


async def user_save(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer(
            'Пожалуйста, отправьте "Да" или "Нет"'
        )
        return
    if message.text.lower() == 'нет':
        await message.answer(
            ('Данные не сохранены.\n'
             'Если необходимо отправить новые данные - нажмите /gks'),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.reset_state()
    buffer_data = await state.get_data()
    station = buffer_data['station']
    user = message.from_user
    station_check = users.find_one({'_id': station})
    if station_check is not None:
        users.update_one(
            {'_id': station},
            {
                '$set':
                {
                    'user_id': user.id,
                    'username': user.full_name
                }
            },
            upsert=False
        )
        await message.answer(
            'Данные отправлены и сохранены.',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.finish()
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=f'Обновлён начальник ГКС: {station}, {user.full_name}'
        )
    else:
        users.insert_one(
            {
                '_id': station,
                'user_id': user.id,
                'username': user.full_name
            }
        )
        await message.answer(
            'Данные отправлены и сохранены.',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.finish()
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=f'Добавлен начальник ГКС: {station}, {user.full_name}'
        )


def register_handlers_service(dp: Dispatcher):
    dp.register_message_handler(reset_handler, commands='reset', state='*')
    dp.register_message_handler(count_users, commands='users')
    dp.register_message_handler(station_choose, commands='gks')
    dp.register_message_handler(
        station_confirm,
        state=GksManager.waiting_station_name
    )
    dp.register_message_handler(
        user_save,
        state=GksManager.waiting_station_confirm
    )
