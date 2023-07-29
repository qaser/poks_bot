from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config.bot_config import dp, bot
from config.mongo_config import admins
from config.telegram_config import MY_TELEGRAM_ID
import utils.constants as const
from aiogram.dispatcher import filters


class Admin(StatesGroup):
    waiting_directions = State()
    waiting_confirm = State()


@dp.message_handler(commands=['admin'])
async def dir_choose(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(f'{const.DONE_EMOJI} Завершить выбор')
        for dir in const.DIRECTIONS_CODES.values():
            keyboard.add(dir)
        await message.answer(
            text=(
                'Выберите направления. Возможен множественный выбор.\n'
                'По завершению нажмите "Завершить выбор"\n\n'
                'Если Вы проходите повторную регистрацию, то вводите все необходимые направления'
            ),
            reply_markup=keyboard,
        )
        await message.delete()
        await state.update_data(dirs=[])
        await Admin.waiting_directions.set()
    else:
        await message.delete()


async def create_dir_list(message: types.Message, state: FSMContext):
    dir_names = const.DIRECTIONS_CODES.values()
    if message.text.lower() != f'{const.DONE_EMOJI} завершить выбор':
        if message.text not in dir_names:
            await message.answer(
                'Пожалуйста, выберите направление, используя список ниже.'
            )
            return
        else:
            for d_code, d_name in const.DIRECTIONS_CODES.items():
                if d_name == message.text:
                    dir_code = d_code
        data = await state.get_data()
        list_dirs = data['dirs']
        if dir_code not in list_dirs:
            list_dirs.append(dir_code)
        await state.update_data(dirs=list_dirs)
        await message.answer(
            text=(
                'Если необходимо выберите ещё направление '
                'или нажмите "Завершить выбор" (самая верхняя кнопка)'
            )
        )
        return
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Нет', 'Да')
        data = await state.get_data()
        dirs = data['dirs']
        if len(dirs) == 0:
            await message.answer('Необходимо выбрать минимум одно направление')
            return
        text_dirs = ''
        for i in dirs:
            name = const.DIRECTIONS_CODES.get(i)
            text_dirs = '{}\n    {}'.format(text_dirs, name)
        await message.answer(
            text=(
                'Вы выбрали направления:\n'
                f'{text_dirs}'
                '\n\nСохранить?'
            ),
            reply_markup=keyboard,
        )
        await Admin.waiting_confirm.set()


async def admin_save(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer(
            'Пожалуйста, отправьте "Да" или "Нет"'
        )
        return
    if message.text.lower() == 'да':
        data = await state.get_data()
        dirs = data['dirs']
        user = message.from_user
        admins.update_one(
            {'user_id': user.id},
            {'$set': {'directions': dirs, 'username': user.full_name}},
            upsert=True
        )
        await message.answer(
            'Администратор добавлен',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.finish()
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=f'Добавлен администратор, {user.full_name}'
        )
    else:
        await message.answer(
            'Данные не сохранены, если необходимо заново пройти регистрацию нажмите /admin',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.finish()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(create_dir_list, state=Admin.waiting_directions)
    dp.register_message_handler(admin_save, state=Admin.waiting_confirm)
