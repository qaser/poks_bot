import asyncio
import datetime as dt
import re

from aiogram_dialog import DialogManager, StartMode
from pyrogram.types import ChatPermissions, ChatPrivileges

import utils.constants as const
from config.bot_config import bot
from config.mongo_config import (admins, emergency_stops, gpa, groups,
                                 otkaz_msgs)
from config.pyrogram_config import app
from config.telegram_config import BOT_ID, MY_TELEGRAM_ID, OTKAZ_GROUP_ID
from dialogs.for_ao.states import Ao
from utils.utils import report_error

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
    await manager.switch_to(Ao.select_stats)


async def on_stats_chosen(callback, widget, manager: DialogManager):
    context = manager.current_context()
    context.dialog_data.update(stats_chosen=widget.widget_id)
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
            'gpa_id': gpa_instance['_id'],
            'is_unfinished_start': False
        }
    ).inserted_id
    await create_group(manager, ao_id, 'dialog')


async def create_group(manager, ao_id, mark):
    ao = emergency_stops.find_one({'_id': ao_id})
    try:
        await app.start()
    except:
        pass
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
    except Exception as e:
        await report_error(e)
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
    except:
        await bot.send_message(
            MY_TELEGRAM_ID,
            text=f'Ссылка для группы "{group_name}" не создана'
        )
    try:
        await add_admin_to_group(BOT_ID, group_id)
    except:
        await bot.send_message(
            MY_TELEGRAM_ID,
            text=f'Бот не смог войти в группу {group_name}'
        )
    admin_users = list(admins.find({
        "$and": [
            {"$or": [{"sub": True}, {"sub": {"$exists": False}}]},
            {"user_id": {"$ne": int(MY_TELEGRAM_ID)}}
        ]
    }))
    invite_text = f'Вас приглашают в чат для расследования АО(ВНО): {link.invite_link}'
    users_in_group = []
    users_with_link = []
    for admin in admin_users:
        admin_id = admin.get('user_id')
        admin_name = admin.get('username')
        try:
            await add_admin_to_group(admin_id, group_id)
            users_in_group.append(admin_name)
            # Задержка между добавлениями
            await asyncio.sleep(1)
        except:
            try:
                await bot.send_message(chat_id=admin_id, text=invite_text)
                users_with_link.append(admin_name)
            except:
                pass
    in_group_text = ', '.join(users_in_group) if len(users_in_group) > 0 else 'отсутствуют'
    with_link_text = ', '.join(users_with_link) if len(users_with_link) > 0 else 'отсутствуют'
    resume_text=(f'Добавлены в группу:\n{in_group_text}\n\n'
                 f'Получили ссылки:\n{with_link_text}')
    try:
        await app.leave_chat(group_id)
    except:
        await bot.send_message(
            MY_TELEGRAM_ID,
            text=f'Почему-то я не покинул группу {group_name}'
        )
    if mark == 'dialog':
        context = manager.current_context()
        context.dialog_data.update(group_id=group_id)
        await replace_messages(manager)
    try:
        msg_link = await bot.send_message(chat_id=OTKAZ_GROUP_ID, text=link.invite_link)
    except:
        await bot.send_message(MY_TELEGRAM_ID, text='Не отправлена ссылка в группу "Отказы"')
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
        otkaz_msgs.insert_one(
            {
                'msg_id': msg_link.message_id,
                'text': link.invite_link,
                'group_id': int(group_id)
            }
        )
        await manager.switch_to(Ao.ao_finish)


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


async def replace_messages(manager):
    context = manager.current_context()
    stats_chosen = context.dialog_data['stats_chosen']
    group_id = context.dialog_data['group_id']
    try:
        msg = otkaz_msgs.find().limit(1).sort([('$natural', -1)])[0]
    except:
        pass
    if stats_chosen == 'stats_enable':
        date_find = re.compile(r'\d\d\.\d\d\.(\d\d\d\d|\d\d)')
        time_find = re.compile(r'(\d|\d\d)\:\d\d')
        try:
            msg = otkaz_msgs.find().limit(1).sort([('$natural', -1)])[0]
            date_text = date_find.search(msg['text']).group()
            result = re.sub(date_text, f'<b><u>{date_text}</u></b>', msg['text'])
            otkaz_msgs.update_one({'_id': msg['_id']}, {'$set': {'text': result}})
        except:
            pass
        try:
            msg = otkaz_msgs.find().limit(1).sort([('$natural', -1)])[0]
            time_text = time_find.search(msg['text']).group()
            result = re.sub(time_text, f'<b><u>{time_text}</u></b>', msg['text'])
            otkaz_msgs.update_one({'_id': msg['_id']}, {'$set': {'text': result}})
        except:
            pass
    try:
        msg = otkaz_msgs.find().limit(1).sort([('$natural', -1)])[0]
    except:
        pass
    try:
        new_msg = await bot.send_message(
            chat_id=OTKAZ_GROUP_ID,
            text=msg['text'],
            parse_mode='HTML'
        )
        await bot.delete_message(
            chat_id=OTKAZ_GROUP_ID,
            message_id=msg['msg_id']
        )
        otkaz_msgs.insert_one(
            {
                'msg_id': new_msg.message_id,
                'text': msg['text'],
                'group_id': int(group_id)
            }
        )
    except:
        pass
