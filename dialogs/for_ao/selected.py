import datetime as dt
import asyncio

from bson import ObjectId
from aiogram_dialog import DialogManager, StartMode
from dialogs.for_ao.states import Ao
from config.pyrogram_config import app
from pyrogram import idle
from pyrogram.types import ChatPrivileges, ChatPermissions
from config.bot_config import bot
from config.telegram_config import MY_TELEGRAM_ID, BOT_ID, OTKAZ_GROUP_ID

from config.mongo_config import emergency_stops, users, admins, gpa, groups
import utils.constants as const

from . import states


async def on_main_menu(callback, widget, manager: DialogManager):
    await manager.start(states.Ao.select_station, mode=StartMode.RESET_STACK)


async def on_station_done(callback, widget, manager: DialogManager, station):
    context = manager.current_context()
    context.dialog_data.update(station=station)
    await manager.switch_to(Ao.select_shop)


async def on_shop_done(callback, widget, manager: DialogManager, shop):
    context = manager.current_context()
    context.dialog_data.update(shop=shop)
    await manager.switch_to(Ao.select_gpa)


async def on_gpa_done(callback, widget, manager: DialogManager, gpa_num):
    context = manager.current_context()
    context.dialog_data.update(gpa=gpa_num)
    await manager.switch_to(Ao.ao_confirm)


async def on_confirm(callback, widget, manager: DialogManager):
    context = manager.current_context()
    station = context.dialog_data['station']
    gpa_num = context.dialog_data['gpa']
    date = dt.datetime.today().strftime('%d.%m.%Y')
    gpa_instance = gpa.find_one({'ks': station, 'num_gpa': gpa_num})
    ao_id = emergency_stops.insert_one(
        {
            'date': date,
            'station': station,
            'gpa': gpa_num,
            'gpa_id': gpa_instance['_id']
        }
    ).inserted_id
    await create_group(manager, ao_id, 'dialog')


async def create_group(manager, ao_id, mark):
    ao = emergency_stops.find_one({'_id': ao_id})
    try:
        app.disconnect()
    except:
        pass
    await app.connect()
    ks = ao.get('station')
    date = ao.get('date')
    gpa_num = ao.get('gpa')
    agr = gpa.find_one({'_id': ao['gpa_id']})
    gpa_name = agr.get('name_gpa') if agr is not None else ''
    ao_count = emergency_stops.count_documents(
        {'gpa_id': ao['gpa_id'], '_id': { '$ne': ao_id }}
    )
    group_name = f'{ks} ГПА{gpa_num} {gpa_name} ({date})'
    try:
        group = await app.create_supergroup(group_name)
    except Exception as err:
        await bot.send_message(
            MY_TELEGRAM_ID,
            text=f'Проблема при создании группы "{group_name}"\n\n{err}'
        )
    group_id = group.id
    groups.insert_one(
        {
            '_id': group_id,
            'group_name': group_name,
            'sub_banned': 'false',
            'ao_id': ao_id,
            'gpa_id': agr['_id']
        }
    )
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
    except Exception as error:
        await bot.send_message(
            MY_TELEGRAM_ID,
            text=f'Ссылка для группы "{group_name}" не создана\n\n{error}'
        )
    try:
        await add_admin_to_group(BOT_ID, group_id)
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
            except:
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
            except:
                users_not_available.append(user_name)
                pass
    in_group_text = ', '.join(users_in_group) if len(users_in_group) > 0 else 'отсутствуют'
    with_link_text = ', '.join(users_with_link) if len(users_with_link) > 0 else 'отсутствуют'
    not_available_text = ', '.join(users_not_available) if len(users_not_available) > 0 else 'отсутствуют'
    resume_text=(f'Добавлены в группу:\n{in_group_text}\n\n'
          f'Получили ссылки:\n{with_link_text}\n\n'
          f'Недоступны:\n{not_available_text}')
    try:
        await app.leave_chat(group_id)
    except:
        await bot.send_message(
            MY_TELEGRAM_ID,
            text=f'Почему-то я не покинул группу {group_name}'
        )
    try:
        await bot.send_message(chat_id=OTKAZ_GROUP_ID, text=link.invite_link)
    except Exception as error:
        await bot.send_message(MY_TELEGRAM_ID, text=error)
    await bot.send_message(MY_TELEGRAM_ID, text=f'Создана группа {group_name}')
    post = await bot.send_message(
        chat_id=group_id,
        text=const.MANUAL,
        parse_mode='HTML'
    )
    try:
        await bot.pin_chat_message(group_id, post.message_id)
        await bot.send_message(group_id, const.NEW_GROUP_TEXT)
    except:
        pass
    if ao_count > 0:
        await send_chat_links(agr, group_id, ao_id)
    if mark == 'dialog':
        context = manager.current_context()
        context.dialog_data.update(resume_text=resume_text)
        await manager.switch_to(Ao.ao_finish)
    await app.disconnect()


async def send_chat_links(agr, group_id, ao_id):
    check_groups = groups.count_documents({'gpa_id': agr['_id'], 'ao_id': { '$ne': ao_id }})
    if check_groups > 0:
        queryset = list(groups.find({'gpa_id': agr['_id'], 'ao_id': { '$ne': ao_id }}))
        for group in queryset:
            try:
                link = await bot.export_chat_invite_link(group['_id'])
                await bot.send_message(group_id, link)
            except:
                pass


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
