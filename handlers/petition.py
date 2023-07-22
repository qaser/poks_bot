import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId

from config.bot_config import bot, dp
from config.mongo_config import admins, users, petitions, buffer
from config.telegram_config import MY_TELEGRAM_ID
from utils.constants import KS
from aiogram.utils.exceptions import CantInitiateConversation
import keyboards.for_petition as kb
import utils.constants as const


class Petition(StatesGroup):
    waiting_petition_text = State()


# точка входа командой /ask
async def direction_select(message: types.Message):
    await message.answer(
        text='Выберите направление деятельности для решения проблемного вопроса',
        reply_markup=kb.directions_kb(),  # коллбэк с приставкой "dir"
    )
    await message.delete()


@dp.callback_query_handler(Text(startswith='dir_'))
async def ask_problem(call: types.CallbackQuery, state: FSMContext):
    _, dir = call.data.split('_')
    dir_name = const.DIRECTIONS_CODES.get(dir)
    await call.message.edit_text(
        text=(
            f'Вы выбрали направление <b>"{dir_name}"</b>\n\n'
            'Введите текст Вашего запроса/предложения/проблемы.\n\n'
            'Сообщение будет отправлено специалисту по выбранному Вами направлению.\n\n'
            # 'Если Вы передумали, то нажмите кнопку <b>Отмена</b>'
        ),
        # reply_markup=kb.cancel_kb(),
        parse_mode=types.ParseMode.HTML
    )

    await state.set_data({'dir': dir, 'msg_id': call.message.message_id})
    await Petition.waiting_petition_text.set()


async def ask_confirmation(message: types.Message, state: FSMContext):
    await state.update_data({'text': message.text})
    data = await state.get_data()
    dir = data['dir']
    msg = data['msg_id']
    msg_id = buffer.insert_one({'text': message.text}).inserted_id
    await state.finish()
    await message.answer(
        text=f'Вы ввели следующий запрос:\n\n<i>"{message.text}"</i>\n\nОтправить?',
        reply_markup=kb.send_kb(dir, msg_id),
        parse_mode=types.ParseMode.HTML
    )
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg)
    # await message.delete()


@dp.callback_query_handler(Text(startswith='ask_'))
async def send_petition(call: types.CallbackQuery, state: FSMContext):
    _, action, dir, msg_id = call.data.split('_')
    msg = buffer.find_one({'_id': ObjectId(msg_id)})
    if action == 'cancel':
        await call.message.edit_text(
            text='Действие отменено.\nЧтобы сделать новый запрос нажмите /ask'
        )
    else:
        dir_name = const.DIRECTIONS_CODES.get(dir)
        user_id = call.message.chat.id
        await call.message.edit_text(
            text=(
                f'Ваш запрос отправлен специалисту по направлению <b>"{dir_name}"</b>\n'
                'Чтобы сделать новый запрос нажмите /ask'
            ),
            parse_mode=types.ParseMode.HTML
        )
        date = dt.datetime.now(tz=const.TZINFO).strftime('%d.%m.%Y %H:%M')
        ks = users.find_one({'user_id': user_id}).get('_id')
        petitions.insert_one(
            {
                'date': date,
                'user_id': user_id,
                'text': msg.get('text'),
                'direction': dir,
                'ks': ks,
                'done': 'false'
            }
        )
    buffer.delete_one({'_id': ObjectId(msg_id)})
    await state.finish()


@dp.callback_query_handler(Text(startswith='cancel'))
async def ask_cancel(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()


def register_handlers_petition(dp: Dispatcher):
    dp.register_message_handler(direction_select, commands='ask')
    dp.register_message_handler(
        ask_confirmation,
        state=Petition.waiting_petition_text
    )
