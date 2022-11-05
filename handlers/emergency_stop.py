import datetime as dt

import pymongo
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config.telegram_config import CHAT_ID_GKS

import utils.constants as const
from config.bot_config import bot
from config.mongo_config import vehicles


class ChooseVehicle(StatesGroup):
    waiting_for_vehicle_type = State()
    waiting_for_vehicle_time = State()
    waiting_for_location = State()
    waiting_comment = State()
    waiting_confirm = State()


class ConfirmVehicleOrder(StatesGroup):
    waiting_for_vehicle_order = State()
    waiting_for_order_comment = State()
    waiting_for_order_confirm = State()


class DeleteVehicleOrder(StatesGroup):
    waiting_for_delete_confirm = State()
    waiting_for_delete_done = State()


# команда /help_gks
async def help_vehicle_message(message: types.Message):
    await message.answer(
        text=(
            'Для создания заявки на технику нажмите /tehnika\n'
            'Для удаления введённой заявки на технику нажмите /tehnika_del\n'
            'Для просмотра списка заявок нажмите /report\n'
            'Для сброса текущего диалога и настроек клавиатуры нажмите /reset\n'
            'Для согласования техники нажмите /confirm\n'
            'Для просмотра согласованной техники нажмите /resume\n'
            'Для отправки отзыва о работе бота или пожеланий нажмите /offer'
        )
    )


# команда /zayavka - перенаправит юзера к боту для заказа техники
async def redirect_vehicle(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id,
        text='Для начала нажмите\n\n/tehnika'
    )


# команда /report - отчёт о заявках техники
async def send_vehicle_report(message: types.Message):
    date = dt.datetime.today().strftime('%d.%m.%Y')
    date_time = dt.datetime.today().strftime('%H:%M')
    queryset = list(vehicles.find({'date': date}))
    if len(queryset) == 0:
        final_message = 'Заявки на технику пока отсутствуют'
    else:
        result = {}
        for i in queryset:
            if result.get(i.get('vehicle')) is None:
                result[i.get('vehicle')] = {}
            result[i.get('vehicle')][i.get('location')] = [
                i.get('time'),
                i.get('comment'),
                i.get('user'),
            ]
        mess = ''
        for vehicle, loc_list in result.items():
            part_message = ''
            for location, data_list in loc_list.items():
                time, comment, user = data_list
                text = '    <b>{}</b> - {}. "{}" <i>({})</i>\n'.format(
                    location,
                    time.lower(),
                    comment,
                    user,
                )
                part_message = '{}{}'.format(part_message, text)
            vehicle_part_text = '<u>{}</u>:\n{}'.format(vehicle, part_message)
            mess = '{}{}\n'.format(mess, vehicle_part_text)
        final_message = '{}\n\n{}'.format(
            f'Заявки на технику {date} по состоянию на {date_time}(мск):',
            mess,
        )
    await message.answer(
        text=final_message,
        parse_mode=types.ParseMode.HTML,
    )


# команда /resume - результаты согласования техники
async def send_vehicle_confirm_resume(message: types.Message):
    date = dt.datetime.today().strftime('%d.%m.%Y')
    queryset = list(vehicles.find({'date': date, 'confirm': True}))
    result = ''
    if len(queryset) == 0:
        result = 'список пуст'
    else:
        for i in queryset:
            vehicle = i.get('vehicle')
            location = i.get('location')
            comment = i.get('confirm_comment')
            text = '<u>{}</u>: <b>{}</b> <i>({})</i>\n'.format(
                vehicle,
                location,
                comment,
            )
            result = '{}{}\n'.format(result, text)
    final_message = '{}\n\n{}'.format(
        'Список согласованной техники:',
        result,
    )
    await message.answer(
        text=final_message,
        parse_mode=types.ParseMode.HTML,
    )


# команда /tehnika - входная точка для заявок техники
async def vehicle_start(message: types.Message):
    if str(message.chat.id) == CHAT_ID_GKS:
        await message.answer(
            text='Эта команда здесь не доступна, нажмите /zayavka',
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for name in const.VEHICLES:
            keyboard.add(name)
        await message.answer(
            text=(
                f'Добрый день {message.from_user.full_name}.\n'
                'Выберите спец.технику из списка ниже'
            ),
            reply_markup=keyboard
        )
        await ChooseVehicle.waiting_for_vehicle_type.set()


async def vehicle_chosen(message: types.Message, state: FSMContext):
    if message.text not in const.VEHICLES:
        await message.answer(
            'Пожалуйста, выберите технику, используя список ниже. '
            'Я не работаю с другой техникой кроме той, что в списке.'
        )
        return
    await state.update_data(chosen_vehicle=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for size in const.PERIODS:
        keyboard.add(size)
    # для простых шагов можно не указывать название состояния, обходясь next()
    await ChooseVehicle.next()
    await message.answer(
        text='Теперь выберите необходимый период времени',
        reply_markup=keyboard
    )


async def vehicle_time_chosen(message: types.Message, state: FSMContext):
    if message.text not in const.PERIODS:
        await message.answer(
            'Пожалуйста, выберите период, используя клавиатуру ниже.'
        )
        return
    await state.update_data(chosen_vehicle_time=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for location in const.LOCATIONS:
        keyboard.add(location)
    await ChooseVehicle.next()
    await message.answer(
        text='Отлично! Выберите место где будет работать техника.',
        reply_markup=keyboard
    )


async def user_location_chosen(message: types.Message, state: FSMContext):
    if message.text not in const.LOCATIONS:
        await message.answer(
            'Пожалуйста, выберите место работы, используя клавиатуру ниже.'
        )
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Без комментария')
    await state.update_data(chosen_location=message.text)
    await message.answer(
        text=('Если необходимо - можете добавить комментарий. '
              'Или нажать на кнопку "Без комментария"'),
        reply_markup=keyboard,
    )
    await ChooseVehicle.next()


async def add_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Нет', 'Да')
    user_data = await state.get_data()
    vehicle = user_data['chosen_vehicle']
    time = user_data['chosen_vehicle_time']
    await message.answer(
        text=f'Вы выбрали "{vehicle}" {time.lower()}.\nВсё верно?',
        reply_markup=keyboard,
    )
    await ChooseVehicle.next()


async def confirmation(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer(
            'Пожалуйста, выберите ответ, используя клавиатуру ниже.'
        )
        return
    if message.text.lower() == 'нет':
        await message.answer(
            ('Хорошо. Данные не сохранены.\n'
             'Если необходимо выбрать технику снова - нажмите /tehnika'),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.reset_state()
    user_data = await state.get_data()
    date = dt.datetime.today().strftime('%d.%m.%Y')
    vehicles.insert_one(
        {
            'date': date,
            'user': message.from_user.full_name,
            'location': user_data['chosen_location'],
            'vehicle': user_data['chosen_vehicle'],
            'time': user_data['chosen_vehicle_time'],
            'comment': user_data['comment'],
            'confirm': False,
            'confirm_comment': '',
        }
    )
    await message.answer(
        ('Отлично! Данные успешно сохранены.\n'
         'Если необходимо выбрать ещё технику нажмите /tehnika'),
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.finish()


async def start_confirm_vehicle_orders(message: types.Message):
    date = dt.datetime.today().strftime('%d.%m.%Y')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    vehicle_orders = list(vehicles.find({'date': date, 'confirm': False}).sort(
        'vehicle',
        pymongo.ASCENDING
    ))
    # добавляем названия кнопок на основе данных из БД
    if len(list(vehicle_orders)) == 0:
        await message.answer(
            ('Список техники для подтверждения пуст.\n'
             'Для формирования отчёта нажмите /resume'),
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        for order in vehicle_orders:
            vehicle = order.get('vehicle')
            location = order.get('location')
            time = order.get('time')
            key = f'{vehicle} | {location} | {time}'
            keyboard.add(key)
        await message.answer(
            text='Выберите технику для подтверждения',
            reply_markup=keyboard,
        )
        await ConfirmVehicleOrder.waiting_for_vehicle_order.set()


async def order_chosen(message: types.Message, state: FSMContext):
    # TODO добавить проверку на корректный ввод названия заказа
    await state.update_data(chosen_order=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Не будет', 'Будет')
    keyboard.add('Без комментария')
    await message.answer(
        text=('Если необходимо - можете добавить комментарий. '
              'Или нажать на кнопку "Без комментария"'),
        reply_markup=keyboard,
    )
    await ConfirmVehicleOrder.next()


async def confirm_comment(message: types.Message, state: FSMContext):
    await state.update_data(confirm_comment=message.text)
    data = await state.get_data()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Нет', 'Да')
    order = data['chosen_order']
    await message.answer(
        text=f'Вы подтверждаете заявку: "{order}".\nВсё верно?',
        reply_markup=keyboard,
    )
    await ConfirmVehicleOrder.next()


async def confirm_order(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer(
            'Пожалуйста, выберите ответ, используя клавиатуру ниже.'
        )
        return
    if message.text.lower() == 'нет':
        await message.answer(
            ('Хорошо. Данные не сохранены.\n'
             'Если необходимо продолжить - нажмите /confirm'),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.reset_state()
    buffer_data = await state.get_data()
    comment = buffer_data['confirm_comment']
    order = buffer_data['chosen_order']
    vehicle, location, time = order.split(' | ')
    date = dt.datetime.today().strftime('%d.%m.%Y')
    vehicles.update_one(
        {
            'date': date,
            'vehicle': vehicle,
            'location': location,
            'time': time,
        },
        {
            '$set': {
                'confirm_comment': comment,
                'confirm': True
            }
        }
    )
    await message.answer(
        ('Отлично! Данные успешно сохранены.\n'
         'Если необходимо продолжить работу с заявками нажмите /confirm\n\n'
         'Если необходим отчёт по заявкам - нажмите /resume'),
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.finish()


async def vehicle_delete(message: types.Message):
    if str(message.chat.id) == CHAT_ID_GKS:
        await message.answer(
            text='Эта команда здесь не доступна, перейдите в чат к боту',
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        date = dt.datetime.today().strftime('%d.%m.%Y')
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        vehicle_orders = list(vehicles.find({'date': date}).sort(
            'location',
            pymongo.ASCENDING
        ))
        # добавляем названия кнопок на основе данных из БД
        if len(list(vehicle_orders)) == 0:
            await message.answer(
                'Заявок пока нет',
                reply_markup=types.ReplyKeyboardRemove()
            )
        else:
            for order in vehicle_orders:
                vehicle = order.get('vehicle')
                location = order.get('location')
                time = order.get('time')
                key = f'{location} | {vehicle} | {time}'
                keyboard.add(key)
            await message.answer(
                text='Выберите заявку для удаления',
                reply_markup=keyboard,
            )
            await DeleteVehicleOrder.waiting_for_delete_confirm.set()


async def vehicle_delete_confirm(message: types.Message, state: FSMContext):
    await state.update_data(chosen_order=message.text)
    data = await state.get_data()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Нет', 'Да')
    order = data['chosen_order']
    await message.answer(
        text=f'Вы подтверждаете удаление заявки?\n\n{order}',
        reply_markup=keyboard,
    )
    await DeleteVehicleOrder.next()


async def vehicle_delete_done(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer(
            'Пожалуйста, выберите ответ, используя клавиатуру ниже.'
        )
        return
    if message.text.lower() == 'нет':
        await message.answer(
            ('Заявка не удалена.\n'
             'Если необходимо выбрать другую заявку - нажмите /tehnika_del'),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.reset_state()
    buffer_data = await state.get_data()
    order = buffer_data['chosen_order']
    location, vehicle, time = order.split(' | ')
    date = dt.datetime.today().strftime('%d.%m.%Y')
    vehicles.delete_one(
        {
            'date': date,
            'vehicle': vehicle,
            'location': location,
            'time': time,
        },
    )
    await message.answer(
        ('Заявка удалена.\n'
         'Если необходимо продолжить удаление заявок нажмите /tehnika_del\n\n'
         'Если Вам необходим список заявок - нажмите /report'),
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.finish()


def register_handlers_vehicle(dp: Dispatcher):
    dp.register_message_handler(help_vehicle_message, commands='help_gks')
    dp.register_message_handler(vehicle_start, commands='tehnika')
    dp.register_message_handler(send_vehicle_report, commands='report')
    dp.register_message_handler(send_vehicle_confirm_resume, commands='resume')
    dp.register_message_handler(redirect_vehicle, commands='zayavka')
    dp.register_message_handler(vehicle_delete, commands='tehnika_del')
    dp.register_message_handler(
        start_confirm_vehicle_orders,
        commands='confirm'
    )
    dp.register_message_handler(
        order_chosen,
        state=ConfirmVehicleOrder.waiting_for_vehicle_order,
    )
    dp.register_message_handler(
        confirm_comment,
        state=ConfirmVehicleOrder.waiting_for_order_comment
    )
    dp.register_message_handler(
        confirm_order,
        state=ConfirmVehicleOrder.waiting_for_order_confirm
    )
    dp.register_message_handler(
        vehicle_chosen,
        state=ChooseVehicle.waiting_for_vehicle_type,
    )
    dp.register_message_handler(
        vehicle_time_chosen,
        state=ChooseVehicle.waiting_for_vehicle_time
    )
    dp.register_message_handler(
        user_location_chosen,
        state=ChooseVehicle.waiting_for_location
    )
    dp.register_message_handler(
        add_comment,
        state=ChooseVehicle.waiting_comment
    )
    dp.register_message_handler(
        confirmation,
        state=ChooseVehicle.waiting_confirm
    )
    dp.register_message_handler(
        vehicle_delete_confirm,
        state=DeleteVehicleOrder.waiting_for_delete_confirm
    )
    dp.register_message_handler(
        vehicle_delete_done,
        state=DeleteVehicleOrder.waiting_for_delete_done
    )
