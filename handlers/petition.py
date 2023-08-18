from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.message import ContentType

import keyboards.for_petition as kb
import utils.constants as const
from config.bot_config import bot, dp
from config.mongo_config import buffer, users


class Petition(StatesGroup):
    waiting_petition_text = State()
    waiting_for_file = State()


# точка входа командой /task
@dp.message_handler(commands=['task'])
async def check_users(message: types.Message):
    if message.chat.type == 'private':
        user_id = message.chat.id
        queryset = list(users.find({'user_id': user_id}))
        if len(queryset) == 0:
            await message.answer('Вам не доступна эта команда')
        elif len(queryset) == 1:
            await direction_select(message)
        else:
            ks_list = [const.KS.index(u['ks']) for u in list(queryset)]
            await message.answer(
                text='Вы зарегистрированы на нескольких КС, выберите одну из списка:',
                reply_markup=kb.ks_user_kb(ks_list)
            )


@dp.callback_query_handler(filters.Text(startswith='task-ks_'))
async def mark_ks(call: types.CallbackQuery, state: FSMContext):
    _, ks_id = call.data.split('_')
    ks = const.KS[int(ks_id)]
    await state.update_data({'ks': ks, 'many_ks': 'true'})
    await direction_select(call.message)


async def direction_select(message: types.Message):
    await message.answer(
        text='Выберите направление деятельности для решения проблемного вопроса',
        reply_markup=kb.directions_kb(),  # коллбэк с приставкой "pet"
    )
    await message.delete()


@dp.callback_query_handler(filters.Text(startswith='pet_'))
async def ask_problem(call: types.CallbackQuery, state: FSMContext):
    _, dir = call.data.split('_')
    dir_name = const.DIRECTIONS_CODES.get(dir)
    await call.message.edit_text(
        text=(
            f'Вы выбрали направление <b>"{dir_name}"</b>\n\n'
            'Введите текст Вашего запроса/предложения/проблемы.\n\n'
            'Сообщение будет отправлено специалисту по выбранному Вами направлению.\n'
            'Если Вы передумали, то нажмите кнопку <b>Отмена</b>'
        ),
        reply_markup=kb.cancel_kb(),
        parse_mode=types.ParseMode.HTML
    )
    await state.update_data({'dir': dir, 'msg': call.message.message_id})
    await Petition.waiting_petition_text.set()


async def ask_confirmation(message: types.Message, state: FSMContext):
    await state.update_data({'text': message.text})
    data = await state.get_data()
    dir = data['dir']
    msg = data['msg']
    if 'many_ks' in data.keys():
        ks = data['ks']
        many_ks = data['many_ks']
        msg_id = buffer.insert_one({'text': message.text, 'ks': ks, 'many_ks': many_ks}).inserted_id
    else:
        msg_id = buffer.insert_one({'text': message.text}).inserted_id
    await state.update_data({'msg_id': msg_id})
    await message.answer(
        text=(f'Вы ввели следующий запрос:\n\n<i>"{message.text}"</i>\n\n'
              'Хотите прикрепить к сообщению документ или фотографию?'),
        reply_markup=kb.upload_choose_kb(dir, msg_id),
        parse_mode=types.ParseMode.HTML
    )
    await bot.delete_message(chat_id=message.from_user.id, message_id=msg)


@dp.callback_query_handler(filters.Text(startswith='upload'), state='*')
async def upload_file_from_user(call: types.CallbackQuery):
    await call.message.edit_text(
        text=('Отправьте фото, видео или документ формата .pdf\n\n'
              'На данный момент можно отправить только один файл'),
    )
    await Petition.waiting_for_file.set()


async def save_file_from_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    num_docs = data.get('num_docs', 0)
    if num_docs < 1:
        docs = data.get('docs', [])
        dir = data['dir']
        msg_id = data['msg_id']
        if message.photo:
            file, file_type = message.photo[-1], 'photo'
        elif message.video:
            file, file_type = message.video, 'video'
        elif message.document:
            if message.document.mime_type == 'application/pdf':
                file, file_type = message.document, 'document'
            else:
                await message.answer('Отправьте пожалуйста документ формата .pdf')
                return
        else:
            await message.answer(
                text=('Данные не загружены. Отправьте пожалуйста фото, '
                      'видео или документ формата .pdf')
            )
            return
        docs.append((file.file_id, file_type))
        await state.update_data({'docs': docs})
        num_docs += 1
        await state.update_data({'num_docs': num_docs})
        await message.answer('Файл получен. Отправить?', reply_markup=kb.send_kb(dir, msg_id))


def register_handlers_petition(dp: Dispatcher):
    dp.register_message_handler(
        ask_confirmation,
        state=Petition.waiting_petition_text
    )
    dp.register_message_handler(
        save_file_from_user,
        state=Petition.waiting_for_file,
        content_types=ContentType.ANY
    )
