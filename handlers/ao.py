import datetime as dt
from time import sleep

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation
from pyrogram.types import ChatPrivileges, ChatPermissions
from config.telegram_config import MY_TELEGRAM_ID, BOT_ID, OTDEL_ID

from config.bot_config import bot, dp
from config.mongo_config import emergency_stops, users, admins, gpa
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
    if message.chat.type == 'private':
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
    gpa_num = data['gpa_num']
    try:
        gpa_instance = gpa.find_one({'ks': station, 'num_gpa': gpa_num})
        gpa_name = gpa_instance.get('name_gpa')
        await state.update_data(gpa_id=gpa_instance.get('_id'))
        gpa_text = f' (по моим данным это {gpa_name})'
    except:
        gpa_text = ''
    await message.answer(
        text=f'Вы выбрали "{station}"\nГПА{gpa_num}{gpa_text}.\nВсё верно?',
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
        try:
            gpa_id = data['gpa_id']
            gpa_instance = gpa.find({'_id': gpa_id})
            ao_list = gpa_instance.get('ao')
            if gpa_instance is not None:
                ao_list.append(ao_id)
            else:
                ao_list = []
            gpa.update_one({'_id': gpa_id}, {'$set': {'ao': ao_list}})
        except:
            pass
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
        gpa_num = ao.get('gpa')
        agr = gpa.find_one({'ks': ks, 'num_gpa': gpa_num})
        gpa_name = agr.get('name_gpa') if agr is not None else ''
        group_name = f'{ks} ГПА{gpa_num} {gpa_name} ({date})'
        msg = await message.answer('Начинается процесс создания рабочего чата...')
        try:
            group = await app.create_supergroup(group_name)
            await bot.send_message(MY_TELEGRAM_ID, text=f'Создана группа {group_name}')
        except Exception as err:
            await msg.edit_text(
                'Возникли проблемы при создании группы, повторите попытку позже'
            )
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Проблема при создании группы "{group_name}"\n\n{err}'
            )
        await msg.edit_text('Группа создана.\nИдет процесс приглашения пользователей...')
        group_id = group.id
        await app.set_chat_protected_content(chat_id=group_id, enabled=True)
        await app.set_chat_permissions(
            chat_id=group_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_send_polls=True,
                can_add_web_page_previews=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        )
        try:
            link = await app.create_chat_invite_link(group_id)
            await bot.send_message(MY_TELEGRAM_ID, text=f'Ссылка для группы "{group_name}" создана')
        except Exception as error:
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Ссылка для группы "{group_name}" не создана\n\n{error}'
            )
        try:
            await add_admin_to_group(BOT_ID, group_id)
            await bot.send_message(MY_TELEGRAM_ID, text=f'Бот в группе {group_name}')
        except Exception as e:
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Бот не смог войти в группу {group_name}\n\n{e}'
            )
        admin_users = list(admins.find({}))
        invite_text = f'Вас приглашают в чат для расследования АО(ВНО): {link.invite_link}'
        users_in_group = []
        users_with_link = []
        users_not_available = []
        for admin in admin_users:
            admin_id = admin.get('user_id')
            admin_name = admin.get('username')
            try:
                if admin_id != 744201326:  # исключаем Батькина
                    await add_admin_to_group(admin_id, group_id)
                    users_in_group.append(admin_name)
                else:
                    await bot.send_message(chat_id=744201326, text=invite_text)
                    users_with_link.append(admin_name)
            except:
                try:
                    await bot.send_message(chat_id=admin_id, text=invite_text)
                    users_with_link.append(admin_name)
                except (BotBlocked, CantInitiateConversation):
                    users_not_available.append(admin_name)
                    pass
        ks_users = list(users.find({'ks': ks}))
        for user in ks_users:
            user_id = user.get('user_id')
            user_name = user.get('username')
            try:
                await app.add_chat_members(group_id, user_id)
                users_in_group.append(user_name)
            except:
                try:
                    await bot.send_message(chat_id=user_id, text=invite_text)
                    users_with_link.append(user_name)
                except (BotBlocked, CantInitiateConversation):
                    users_not_available.append(user_name)
                    pass
        in_group_text = ', '.join(users_in_group) if len(users_in_group) > 0 else 'отсутствуют'
        with_link_text = ', '.join(users_with_link) if len(users_with_link) > 0 else 'отсутствуют'
        not_available_text = ', '.join(users_not_available) if len(users_not_available) > 0 else 'отсутствуют'
        await msg.edit_text(
            text=(f'Добавлены в группу:\n{in_group_text}\n\n'
                  f'Получили ссылки:\n{with_link_text}\n\n'
                  f'Недоступны:\n{not_available_text}')
        )
        await message.answer(link.invite_link)
        try:
            await app.leave_chat(group_id)
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Я покинул группу {group_name}'
            )
        except:
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Почему-то я не покинул группу {group_name}'
            )
        try:
            await bot.send_message(chat_id=OTDEL_ID, text=link.invite_link)
        except Exception as error:
            await bot.send_message(MY_TELEGRAM_ID, text=error)


async def add_admin_to_group(user_id, group_id):
    await app.promote_chat_member(
        chat_id=group_id,
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


@dp.message_handler(commands=['copy'])
async def hash_users(message: types.Message):
    await message.delete()
    async with app:
        try:
            await app.promote_chat_member(
                chat_id=message.chat.id,
                user_id=MY_TELEGRAM_ID,
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
                    is_anonymous=True
                )
            )
        except Exception as e:
            await bot.send_message(MY_TELEGRAM_ID, text=e)
        try:
            await app.set_chat_protected_content(
                chat_id=message.chat.id,
                enabled=False
            )
            msg = await message.answer('30', disable_notification=True)
            for sec in range(29, 0, -2):
                await msg.edit_text(sec)
                sleep(2)
        except Exception as err:
            await bot.send_message(MY_TELEGRAM_ID, text=err)
        try:
            await app.set_chat_protected_content(
                chat_id=message.chat.id,
                enabled=True
            )
        except Exception as error:
            await bot.send_message(MY_TELEGRAM_ID, text=error)
        try:
            await msg.delete()
        except:
            pass
        try:
            await app.leave_chat(message.chat.id)
        except Exception as er:
            await bot.send_message(MY_TELEGRAM_ID, text=er)



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
