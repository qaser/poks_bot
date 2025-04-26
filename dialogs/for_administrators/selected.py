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


async def on_paths(callback, widget, manager: DialogManager):
    await manager.switch_to(Admins.paths_info)


async def on_path_selected(callback, widget, manager: DialogManager):
    context = manager.current_context()
    _, _, path_type = widget.widget_id.split('_')
    context.dialog_data.update(path_type=path_type)
    await manager.switch_to(Admins.select_num_stages)


async def on_num_stages_selected(callback, widget, manager: DialogManager):
    context = manager.current_context()
    _, _, num_stages = widget.widget_id.split('_')
    context.dialog_data.update(num_stages=num_stages)
    await manager.switch_to(Admins.select_majors)


async def back_and_erase_widget_click(callbac, button, manager: DialogManager):
    widget = manager.find('s_majors')
    await widget.reset_checked()
    await manager.back()


async def on_majors_done(callback, widget, manager: DialogManager):
    context = manager.current_context()
    widget = manager.find('s_majors')
    context.dialog_data.update(majors=widget.get_checked())
    await manager.switch_to(Admins.path_confirm)


async def path_save(callback, widget, manager: DialogManager):
    context = manager.current_context()
    num_stages = int(context.dialog_data['num_stages'])
    majors = context.dialog_data['majors']
    path_name = const.PATH_TYPE[context.dialog_data['path_type']]
    stages = {}
    for stage_num in range(1, num_stages + 1):
        stages[str(stage_num)] = int(majors[stage_num - 1])
    paths.update_one(
        {'path_type': path_name},
        {'$set': {'num_stages': num_stages, 'stages': stages}},
        upsert=True
    )
    widget = manager.find('s_majors')
    await widget.reset_checked()
    await manager.switch_to(Admins.path_complete)
