import datetime as dt
import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.bot_config import bot
from config.mongo_config import emergency_stops, users
from utils.constants import KS


async def send_exam_answers(message: types.Message):
    media = types.MediaGroup()
    for _, _, files in os.walk('static/tutorial/'):
        for filename in files:
            file = f'static/tutorial/{filename}'
            media.attach_photo(types.InputFile(file))
    await bot.send_media_group(message.chat.id, media=media)


class Emergency(StatesGroup):
    waiting_station_name = State()
    waiting_gpa_number = State()
    waiting_confirm = State()


# команда /ao - входная точка для оповещения аварийного останова
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
    gks_manager = users.find_one({'_id': message.text})
    if gks_manager is None:
        await message.answer(
            text=('В базе данных нет информации о начальнике ГКС '
                  'с этой станции.\nОперация прервана.'),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.finish()
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
        text=f'Вы выбрали "{station}"\nГПА {gpa}\nВсё верно?',
        reply_markup=keyboard,
    )
    await Emergency.next()


async def confirmation(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer(
            'Пожалуйста, выберите ответ, используя клавиатуру ниже.'
        )
        return
    if message.text.lower() == 'нет':
        await message.answer(
            ('Данные не сохранены.\n'
             'Если необходимо повторить команду - нажмите /ao'),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.reset_state()
    date = dt.datetime.today().strftime('%d.%m.%Y')
    data = await state.get_data()
    emergency_stops.insert_one(
        {
            'date': date,
            'station': data['station'],
            'gpa': data['gpa_num'],
        }
    )
    gks_manager = users.find_one({'_id': data['station']})
    username = gks_manager.get('username')
    user_id = gks_manager.get('user_id')
    await bot.send_message(
        chat_id=user_id,
        text=(
                f'{data["station"]}. Произошёл АО ГПА{data["gpa_num"]}.\n'
                'Вам отправлены инструкции по организации рабочего чата.'
        ),
        reply_markup=types.ReplyKeyboardRemove()
    )
    file_pdf = open('static/tutorial_pdf/инструкция' + '.pdf', 'rb')
    await bot.send_document(chat_id=user_id, document=file_pdf)
    await message.answer(
        text=(
                'Принято. Сообщение с инструкциями отправлено.\n'
                f'Адресат: {username}'
        ),
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.finish()


def register_handlers_emergency(dp: Dispatcher):
    dp.register_message_handler(emergency_start, commands='ao')
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
