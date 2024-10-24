from aiogram import F, Router
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import utils.constants as const
from config.bot_config import bot
from config.mongo_config import admins
from config.telegram_config import MY_TELEGRAM_ID
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


router = Router()

class Admin(StatesGroup):
    waiting_directions = State()
    waiting_confirm = State()


@router.message(Command('admin'))
async def dir_choose(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        kb = ReplyKeyboardBuilder()
        kb.button(text='Завершить выбор')
        kb.button(text='Выбрать все направления')
        for dir in const.DIRECTIONS_CODES.values():
            kb.button(text=dir)
        kb.adjust(1)
        await message.answer(
            text=(
                'Выберите направления. Возможен множественный выбор.\n'
                'По завершению нажмите "Завершить выбор"\n'
                'Для выбора сразу всех направлений нажмите кнопку "Выбрать все направления"\n\n'
                'Если Вы проходите повторную регистрацию, то вводите все необходимые направления'
            ),
            reply_markup=kb.as_markup(resize_keyboard=True),
        )
        await message.delete()
        await state.update_data(dirs=[])
        await state.set_state(Admin.waiting_directions)
    else:
        await message.delete()


@router.message(Admin.waiting_directions)
async def create_dir_list(message: types.Message, state: FSMContext):
    dir_names = const.DIRECTIONS_CODES.values()
    if message.text.lower() == f'выбрать все направления':
        dirs = list(const.DIRECTIONS_CODES.keys())
        await state.update_data(dirs=dirs)
    elif message.text.lower() != f'завершить выбор':
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
        data = await state.get_data()
        dirs = data['dirs']
        if len(dirs) == 0:
            await message.answer('Необходимо выбрать минимум одно направление')
            return
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='Нет')
    keyboard.button(text='Да')
    text_dirs = ''
    keyboard.adjust(2)
    for i in dirs:
        name = const.DIRECTIONS_CODES.get(i)
        text_dirs = '{}\n    {}'.format(text_dirs, name)
    await message.answer(
        text=(
            'Вы выбрали направления:\n'
            f'{text_dirs}'
            '\n\nСохранить?'
        ),
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )
    await state.set_state(Admin.waiting_confirm)


@router.message(Admin.waiting_confirm)
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
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=f'Добавлен администратор, {user.full_name}'
        )
    else:
        await message.answer(
            'Данные не сохранены, если необходимо заново пройти регистрацию нажмите /admin',
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
