import datetime as dt
import functools
import inspect

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.bot_config import bot
from config.mongo_config import admins, emergency_stops, users
from config.telegram_config import MY_TELEGRAM_ID
from texts.initial import MANUAL, REPORT
from utils.constants import KS
from aiogram.utils.exceptions import CantInitiateConversation


class Emergency(StatesGroup):
    waiting_station_name = State()
    waiting_gpa_number = State()
    waiting_confirm = State()


def admin_check(f):
    @functools.wraps(f)
    async def wrapped_func(*args, **kwargs):
        func_args = inspect.getcallargs(f, *args, **kwargs)
        post = func_args['message']
        if admins.find_one({'user_id': post.from_user.id}) is None:
            try:
                await bot.send_message(
                    post.from_user.id,
                    'Вам не доступна эта команда'
                )
                await bot.send_message(
                    MY_TELEGRAM_ID,
                    f'Пользователь {post.from_user.full_name} ввёл {post.text}'
                )
            except:
                pass
        else:
            return await f(*args, **kwargs)
    return wrapped_func


# команда /ao - входная точка для оповещения аварийного останова
@admin_check
async def emergency_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for station in KS:
        keyboard.add(station)
    await message.answer(
        text=(
            'Выберите компрессорную станцию, '
            'на которой произошёл аварийный останов'
        ),
        reply_markup=keyboard
    )
    await Emergency.waiting_station_name.set()


async def station_name(message: types.Message, state: FSMContext):
    if message.text not in KS:
        await message.answer(
            'Пожалуйста, выберите КС, используя список ниже. '
            'Я не работаю с другими объектами кроме тех, что в списке.'
        )
        return
    else:
        await state.update_data(station=message.text)
        await message.answer(
            text='Введите номер ГПА',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await Emergency.next()


async def gpa_number(message: types.Message, state: FSMContext):
    await state.update_data(gpa_num=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Нет', 'Да')
    data = await state.get_data()
    station = data['station']
    gpa = data['gpa_num']
    await message.answer(
        text=f'Вы выбрали "{station}"\nГПА {gpa}.\nВсё верно?',
        reply_markup=keyboard,
    )
    await Emergency.next()


async def confirmation(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer(
            'Пожалуйста, выберите ответ, используя клавиатуру ниже.'
        )
        return
    if message.text.lower() == 'да':
        date = dt.datetime.today().strftime('%d.%m.%Y')
        data = await state.get_data()
        emergency_stops.insert_one(
            {
                'date': date,
                'station': data['station'],
                'gpa': data['gpa_num'],
            }
        )
        nach_gks = users.find_one({'ks': data['station'], 'prof': 'nachgks'})
        username = nach_gks.get('username')
        user_id = nach_gks.get('user_id')
        msg_text = (f'{data["station"]}.\nДля расследования АО ГПА{data["gpa_num"]} '
                    'Вам отправлена инструкция по организации рабочего чата.')
        file_pdf = open('static/tutorial_pdf/Инструкция' + '.pdf', 'rb')
        try:
            await bot.send_message(chat_id=user_id, text=msg_text)
            await bot.send_document(chat_id=user_id, document=file_pdf)
            await message.answer(
                text=f'Принято. Сообщение с инструкциями отправлено.\nАдресат: {username}',
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.finish()
        except CantInitiateConversation:
            zamnach_gks = users.find_one({'ks': data['station'], 'prof': 'znachgks'})
            if zamnach_gks is None:
                await message.answer(
                    text=(f'Бот не может отправить сообщение пользователю "{username}".\n'
                        'Вероятно пользователь заблокировал бота.\n'
                        'Информация о заместителе отсутствует в БД.\n'
                        'Свяжитесь с пользователем, а потом повторите попытку.'),
                    reply_markup=types.ReplyKeyboardRemove()
                )
            else:
                await message.answer(
                    text=(f'Бот не может отправить сообщение пользователю "{username}".\n'
                        'Вероятно пользователь заблокировал бота.\n'
                        'Пытаюсь отправить его заместителю...'),
                    reply_markup=types.ReplyKeyboardRemove()
                )
                try:
                    username = zamnach_gks.get('username')
                    user_id = zamnach_gks.get('user_id')
                    await bot.send_message(chat_id=user_id, text=msg_text)
                    await bot.send_document(chat_id=user_id, document=file_pdf)
                    await message.answer(
                        text=('Принято. Сообщение с инструкциями отправлено.\nАдресат: {username}'),
                        reply_markup=types.ReplyKeyboardRemove()
                    )
                    await state.finish()
                except CantInitiateConversation:
                    await message.answer(
                        text=(f'Бот не может отправить сообщение пользователю "{username}".\n'
                            'Вероятно пользователь заблокировал бота.\n'
                            'Свяжитесь с пользователем, а потом повторите попытку.'),
                        reply_markup=types.ReplyKeyboardRemove()
                    )
                    await state.finish()
    else:
        await message.answer(
            ('Данные не сохранены.\n'
             'Если необходимо повторить команду - нажмите /ao'),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.finish()



#  обработка команды /manual
# async def send_manual(message: types.Message):
#     if message.chat.id == -1001856019654:
#         await message.answer('Эта команда здесь не доступна, перейдите к боту @otdel_ks_bot')
#     else:
#         post = await message.answer(
#             MANUAL,
#             parse_mode=types.ParseMode.HTML,
#         )
#         try:
#             await bot.pin_chat_message(message.chat.id, post.message_id)
#         except:
#             pass


#  обработка команды /report
async def send_report(message: types.Message):
    if message.chat.id == -1001856019654:
        await message.answer('Эта команда здесь не доступна, перейдите к боту @otdel_ks_bot')
    else:
        await message.answer(REPORT)


def register_handlers_emergency(dp: Dispatcher):
    dp.register_message_handler(emergency_start, commands='ao')
    # dp.register_message_handler(send_manual, commands='manual')
    dp.register_message_handler(send_report, commands='report')
    dp.register_message_handler(
        station_name,
        state=Emergency.waiting_station_name
    )
    dp.register_message_handler(
        gpa_number,
        state=Emergency.waiting_gpa_number
    )
    dp.register_message_handler(
        confirmation,
        state=Emergency.waiting_confirm
    )
