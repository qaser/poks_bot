from collections import Counter

from aiogram_dialog import DialogManager
from bson.objectid import ObjectId

from config.mongo_config import admins, emergency_stops, gpa, users
from utils.constants import KS


async def get_stations(dialog_manager: DialogManager, **middleware_data):
    return {'stations': KS}


async def get_shops(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    station = context.dialog_data['station']
    queryset = gpa.find({'ks': station}).distinct('num_shop')
    return {'shops': queryset}


async def get_gpa(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    shop = context.dialog_data['shop']
    station = context.dialog_data['station']
    queryset = gpa.find({'ks': station, 'num_shop': shop}).distinct('num_gpa')
    return {'gpa': queryset}


async def get_ao_info(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    num_gpa = context.dialog_data['gpa']
    station = context.dialog_data['station']
    gpa_instance = gpa.find_one({'ks': station, 'num_gpa': num_gpa})
    ao_count = emergency_stops.count_documents({'gpa_id': gpa_instance['_id']})
    return {
        'station': station,
        'gpa_num': num_gpa,
        'gpa_name': gpa_instance['name_gpa'],
        'ao_count': ao_count,
        'ao_not_null': True if ao_count > 0 else False
    }


async def get_users_info(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    try:
        users_info = context.dialog_data['resume_text']
    except:
        users_info = None
    no_users_info = True if users_info is None else False
    return {'users_info': users_info, 'no_users_info': no_users_info}
