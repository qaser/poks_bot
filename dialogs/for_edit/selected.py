import asyncio

from aiogram_dialog import DialogManager

from config.bot_config import bot
from config.mongo_config import emergency_stops, groups, otkaz_msgs
from config.pyrogram_config import app
from config.telegram_config import OTKAZ_GROUP_ID
from dialogs.for_edit.states import Edit
from utils.utils import report_error


async def on_group_done(callback, widget, manager: DialogManager, group_id):
    context = manager.current_context()
    context.dialog_data.update(group_id=group_id)
    await manager.switch_to(Edit.delete_confirm)


async def on_confirm(callback, widget, manager: DialogManager):
    context = manager.current_context()
    group_id = context.dialog_data['group_id']
    group = groups.find_one({'_id': int(group_id)})
    emergency_stops.delete_one({'_id': group['ao_id']})
    groups.delete_one({'_id': int(group_id)})
    msgs = list(otkaz_msgs.find({'group_id': int(group_id)}))
    for msg in msgs:
        try:
            await bot.delete_message(OTKAZ_GROUP_ID, msg['msg_id'])
        except:
            pass
    otkaz_msgs.delete_many({'group_id': int(group_id)})
    await delete_group_members(int(group_id))
    await manager.switch_to(Edit.finish_delete)


async def delete_group_members(group_id):
    try:
        await app.start()
    except:
        pass
    try:
        link = await app.create_chat_invite_link(group_id)
        await app.join_chat(link.invite_link)
    except:
        pass
    user_ids = await get_all_members(app, group_id)
    for user_id in user_ids:
        try:
            await app.kick_chat_member(group_id, user_id)
            await asyncio.sleep(1)  # Чтобы не получить FloodWait
        except Exception as e:
            await report_error(e)


async def get_all_members(app, chat_id):
    """Получаем список всех участников чата"""
    members = []
    async for member in app.get_chat_members(chat_id):
        members.append(member.user.id)
    return members
