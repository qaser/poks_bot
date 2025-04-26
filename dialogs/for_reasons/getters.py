import re

from aiogram_dialog import DialogManager
from config.bot_config import bot

from config.mongo_config import emergency_stops, gpa, groups
from utils.constants import KS


async def get_stations(dialog_manager: DialogManager, **middleware_data):
    return {'stations': KS}


async def get_gpa(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    station = context.dialog_data['station']
    queryset = emergency_stops.find({'station': station}).distinct('gpa')
    return {'gpa': queryset}


async def get_groups_links(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    station = context.dialog_data['station']
    gpa_num = context.dialog_data['gpa']
    gpa_id = gpa.find_one({'ks': station, 'num_gpa': gpa_num}).get('_id')
    queryset = list(groups.find({'gpa_id': gpa_id}))
    links = []
    for group in queryset:
        try:
            invite_link = await bot.create_chat_invite_link(chat_id=group['_id'])
            links.append((remove_ks_prefix(group['group_name']), invite_link.invite_link))
        except Exception as e:
            pass
    len_links = len(links)
    return {
        'links': links,
        'empty': True if len_links == 0 else False,
        'not_empty': True if len_links > 0 else False,
        'is_paginated': True if len_links > 6 else False,
    }


def remove_ks_prefix(input_string):
    # Удаляем первое слово и следующее за ним "КС" (с любыми пробелами/знаками)
    result = re.sub(r'^\S+\s+КС\s*', '', input_string)
    return result.strip()
