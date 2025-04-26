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


async def get_request_info(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    num_gpa = context.dialog_data['gpa']
    station = context.dialog_data['station']
    gpa_instance = gpa.find_one({'ks': station, 'num_gpa': num_gpa})
    return {
        'station': station,
        'gpa_num': num_gpa,
        'gpa_name': gpa_instance['name_gpa'],
        'request_text': context.dialog_data['request_text'],
    }
