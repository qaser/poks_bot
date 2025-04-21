import re

from aiogram_dialog import DialogManager
from config.bot_config import bot

from config.mongo_config import emergency_stops, groups


async def get_groups(dialog_manager: DialogManager, **middleware_data):
    queryset = list(groups.find({}).sort('$natural', -1).limit(5))
    res = [(group['group_name'], group['_id']) for group in queryset]
    return {'groups': res}


async def get_group_info(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    group_id = context.dialog_data['group_id']
    group = groups.find_one({'_id': int(group_id)})
    return {'group_name': group['group_name']}
