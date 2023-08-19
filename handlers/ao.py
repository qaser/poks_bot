import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation
from pyrogram.types import ChatPrivileges
from config.telegram_config import MY_TELEGRAM_ID, BOT_ID

from config.bot_config import bot, dp
from config.mongo_config import emergency_stops, users, admins
from config.pyrogram_config import app
from utils.constants import KS
from utils.decorators import admin_check


class Ao(StatesGroup):
    waiting_station_name = State()
    waiting_gpa_number = State()
    waiting_confirm = State()


# команда /ao - входная точка для оповещения аварийного останова
@admin_check
@dp.message_handler(commands=['es'])
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
    await message.delete()
    await Ao.waiting_station_name.set()


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
        await Ao.next()


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
    await Ao.next()


async def confirmation(message: types.Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer(
            'Пожалуйста, выберите ответ, используя клавиатуру ниже.'
        )
        return
    if message.text.lower() == 'да':
        date = dt.datetime.today().strftime('%d.%m.%Y')
        data = await state.get_data()
        ao_id = emergency_stops.insert_one(
            {
                'date': date,
                'station': data['station'],
                'gpa': data['gpa_num'],
            }
        ).inserted_id
        await state.finish()
        await message.answer(
            text=f'Принято',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await create_group(ao_id, message)
    else:
        await message.answer(
            ('Данные не сохранены.\n'
             'Если необходимо повторить команду - нажмите /es'),
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.finish()


async def create_group(ao_id, message: types.Message):
    ao = emergency_stops.find_one({'_id': ao_id})
    async with app:
        ks = ao.get('station')
        date = ao.get('date')
        gpa = ao.get('gpa')
        group_name = f'{ks} ГПА{gpa} ({date})'
        msg = await message.answer('Начинается процесс создания рабочего чата...')
        try:
            group = await app.create_supergroup(group_name)
            group_id = group.id
            link = await app.create_chat_invite_link(group_id)
            await bot.send_message(MY_TELEGRAM_ID, text=f'Создана группа {group_name}')
            await msg.edit_text('Группа создана.\nИдет процесс приглашения пользователей...')
        except:
            await msg.edit_text(
                'Возникли проблемы при создании группы, повторите попытку позже'
            )
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Проблема при создании {group_name}'
            )
        await add_admin_to_group(BOT_ID, group_id)
        admin_users = list(admins.find({}))
        invite_text = f'Вас приглашают в чат для расследования АО(ВНО): {link.invite_link}'
        for admin in admin_users:
            admin_id = admin.get('user_id')
            try:
                await add_admin_to_group(admin_id, group_id)
                await bot.send_message(chat_id=admin_id, text=invite_text)
            except (BotBlocked, CantInitiateConversation):
                pass
        ks_users = list(users.find({'ks': ks}))
        await msg.edit_text('Пользователи добавлены.\nПочти готово...')
        for user in ks_users:
            user_id = user.get('user_id')
            try:
                await app.add_chat_members(group_id, user_id)
                await bot.send_message(chat_id=user_id, text=invite_text)
            except (BotBlocked, CantInitiateConversation):
                pass
        await msg.delete()
        try:
            await app.leave_chat(group_id)
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Я удачно покинул группу {group_name}'
            )
        except:
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Почему-то я не покинул группу {group_name}'
            )


async def add_admin_to_group(user_id, group_id):
    await app.promote_chat_member(
        chat_id= group_id,
        user_id=user_id,
        privileges=ChatPrivileges(
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=True,
            can_change_info=True,
            can_post_messages=True,
            can_edit_messages=True,
            can_invite_users=True,
            can_pin_messages=True,
            is_anonymous=False
        )
    )


def register_handlers_ao(dp: Dispatcher):
    dp.register_message_handler(
        station_name,
        state=Ao.waiting_station_name
    )
    dp.register_message_handler(
        gpa_number,
        state=Ao.waiting_gpa_number
    )
    dp.register_message_handler(
        confirmation,
        state=Ao.waiting_confirm
    )
