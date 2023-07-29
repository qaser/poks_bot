import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.bot_config import bot, dp
from config.mongo_config import bugs
from config.telegram_config import MY_TELEGRAM_ID


class Bugs(StatesGroup):
    waiting_for_bug = State()
    waiting_for_bug_confirm = State()


# обработка команды /bugs - отзывы и предложения
@dp.message_handler(commands=['bugs'])
async def bot_bug(message: types.Message):
    if message.chat.type == 'private':
        await message.answer(
            text=(
                'Если Вы обнаружили ошибки в работе бота или '
                'у Вас есть предложения по улучшению его работы - '
                'напишите о них в следующем сообщении'
            ),
        )
        await Bugs.waiting_for_bug.set()


async def add_bug(message: types.Message, state: FSMContext):
    await state.update_data(bug=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Нет', 'Да')
    await message.answer(
        text='Вы точно хотите отправить отзыв о работе бота?',
        reply_markup=keyboard,
    )
    await Bugs.waiting_for_bug_confirm.set()


async def confirm_bug(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer(
            'Пожалуйста, отправьте "Да" или "Нет"'
        )
        return
    if message.text.lower() == 'да':
        buffer_data = await state.get_data()
        bug_text = buffer_data['bug']
        user = message.from_user
        date = dt.datetime.today().strftime('%d.%m.%Y %H:%M')
        bugs.insert_one(
            {
                'date': date,
                'user_id': user.id,
                'text': bug_text,
            }
        )
        await message.answer(
            text='Отлично! Сообщение отправлено.',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.finish()
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=f'Получен новый отзыв от {user.full_name}:\n{bug_text}'
        )
    else:
        await message.answer(
            ('Хорошо. Отзыв не сохранен.\n'
             'Если необходимо отправить новый отзыв - нажмите /bugs'),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.reset_state()


def register_handlers_bugs(dp: Dispatcher):
    dp.register_message_handler(add_bug, state=Bugs.waiting_for_bug)
    dp.register_message_handler(
        confirm_bug,
        state=Bugs.waiting_for_bug_confirm
    )
