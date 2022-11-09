from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.bot_config import bot
from config.mongo_config import admins, groups, users
from config.telegram_config import MY_TELEGRAM_ID
from handlers.emergency_stop import admin_check
from utils.constants import KS


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
    user_id = message.from_user.id
    check = admin_check(user_id)
    if check:
        queryset = list(users.find({}))
        users_count = len(queryset)
        final_text = ''
        for user in queryset:
            username = '{}, {}'.format(user['_id'], user['username'])
            final_text = '{}\n\n{}'.format(username, final_text)
        await message.answer(
            text=f'Количество пользователей в БД: {users_count}\n\n{final_text}'
        )
    else:
        await message.answer('Вам недоступна эта команда')


# обработка команды /gks - сбор данных о начальниках ГКС
async def station_choose(message: types.Message):
    if message.chat.id == -1001856019654:
        await message.answer('Эта команда здесь не доступна, перейдите к боту @otdel_ks_bot')
    else:
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
    if message.text not in KS:
        await message.answer(
            'Пожалуйста, выберите КС, используя список ниже.'
        )
        return
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


# запрет на рассылку уведомлений
async def stop_subscribe(message: types.Message):
    user_id = message.from_user.id
    check = admin_check(user_id)
    if check:
        group_id = message.chat.id
        group_check = groups.find_one({'_id': group_id})
        if group_check is not None:
            groups.update_one(
                {'_id': group_id},
                {
                    '$set':
                    {
                        'sub_banned': 'true',
                    }
                },
                upsert=False
            )
            await message.answer('Напоминания для этой группы отключены')
        else:
            await message.answer(
                'Информации об этой группе не найдено.\n'
                'Удалите бота из группы, а затем снова добавьте'
            )
    else:
        await message.answer('Вам недоступна эта команда')


# включение рассылки уведомлений
async def start_subscribe(message: types.Message):
    user_id = message.from_user.id
    check = admin_check(user_id)
    if check:
        group_id = message.chat.id
        group_check = groups.find_one({'_id': group_id})
        if group_check is not None:
            groups.update_one(
                {'_id': group_id},
                {
                    '$set':
                    {
                        'sub_banned': 'false',
                    }
                },
                upsert=False
            )
            await message.answer('Напоминания для этой группы включены')
        else:
            await message.answer(
                'Информации об этой группе не найдено.\n'
                'Удалите бота из группы, а затем снова добавьте'
            )
    else:
        await message.answer('Вам недоступна эта команда')


async def set_admin(message: types.Message):
    user = message.from_user
    admins.insert_one(
        {
            'user_id': user.id,
            'username': user.full_name
        }
    )
    await message.answer('Администратор добавлен')


def register_handlers_service(dp: Dispatcher):
    dp.register_message_handler(reset_handler, commands='reset', state='*')
    dp.register_message_handler(count_users, commands='users')
    dp.register_message_handler(stop_subscribe, commands='unsub')
    dp.register_message_handler(start_subscribe, commands='sub')
    dp.register_message_handler(station_choose, commands='gks')
    dp.register_message_handler(set_admin, commands='admin')
    dp.register_message_handler(
        station_confirm,
        state=GksManager.waiting_station_name
    )
    dp.register_message_handler(
        user_save,
        state=GksManager.waiting_station_confirm
    )
