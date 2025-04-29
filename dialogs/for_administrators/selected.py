import datetime as dt

from aiogram_dialog import DialogManager, StartMode

import utils.constants as const
from config.bot_config import bot
from config.mongo_config import admins, paths
from config.telegram_config import MY_TELEGRAM_ID
from dialogs.for_administrators.states import Admins


async def on_main_menu(callback, widget, manager: DialogManager):
    await manager.start(Admins.select_admin, mode=StartMode.RESET_STACK)


async def on_admins_list(callback, widget, manager: DialogManager):
    await manager.switch_to(Admins.select_admin)


async def on_select_admin(callback, widget, manager: DialogManager, admin_id):
    context = manager.current_context()
    context.dialog_data.update(admin_id=admin_id)
    await manager.switch_to(Admins.show_admin)


async def update_admin_info(callback, widget, manager: DialogManager):
    context = manager.current_context()
    admin_id = context.dialog_data['admin_id']
    username = manager.event.from_user.full_name
    admins.update_one(
        {'user_id': int(admin_id)},
        {'$set': {'username': username}},
        upsert=False,
    )
    await manager.switch_to(Admins.show_admin)


async def update_admin_sub(callback, widget, manager: DialogManager):
    context = manager.current_context()
    admin_id = context.dialog_data['admin_id']
    admins.update_one(
        {'user_id': int(admin_id)},
        [{'$set': {'sub': {'$not': {'$ifNull': ['$sub', True]}}}}],
        upsert=True
    )
    await manager.switch_to(Admins.show_admin)


async def confirm_delete_admin(callback, widget, manager: DialogManager):
    await manager.switch_to(Admins.delete_confirm)


async def delete_admin(callback, widget, manager: DialogManager):
    context = manager.current_context()
    admin_id = context.dialog_data['admin_id']
    admins.delete_one({'user_id': int(admin_id)})
    await manager.start(Admins.select_admin, mode=StartMode.RESET_STACK)
