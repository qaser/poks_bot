import datetime as dt
from collections import Counter

from aiogram_dialog import DialogManager
from bson.objectid import ObjectId
from dateutil.relativedelta import relativedelta

from config.mongo_config import (admins, emergency_stops, gpa, operating_time,
                                 users)
from utils import constants as const


async def get_last_report(dialog_manager: DialogManager, **middleware_data):
    # user_id = dialog_manager.event.from_user.id
    context = dialog_manager.current_context()
    date = dt.datetime.now()
    prev_month = date - relativedelta(months=1)
    pipeline = [
        {'$lookup': {'from': 'operating_time', 'localField': '_id', 'foreignField': 'gpa_id', 'as': 'working_data'}},
        {'$unwind': '$working_data'},
        {'$match': {'working_data.year': prev_month.year, 'working_data.month': prev_month.month}},
        {'$group': {'_id': '$ks', 'gpa_ids': {'$push': "$_id"}}},
        {'$project': {'_id': 0, 'ks': '$_id', 'gpa_ids': 1}},
        {'$sort': {'ks': 1}}
    ]
    queryset = list(gpa.aggregate(pipeline))
    saved_index = context.dialog_data.get('index_num')
    index_num = 0 if saved_index is None else saved_index
    index_sum = len(queryset)
    if index_sum > 0:
        context.dialog_data.update(index_sum=index_sum)
        context.dialog_data.update(index_num=index_num)
        ks_data = queryset[index_num]
        gpa_ids = ks_data['gpa_ids']
        sum_time = 0
        report_text = ''
        nav_is_on = True if index_sum > 1 else False
        for gpa_id in gpa_ids:
            w_time = operating_time.find_one(
                {'gpa_id': gpa_id, 'month': prev_month.month, 'year': prev_month.year}
            )['work_time']
            num_gpa = gpa.find_one({'_id': gpa_id}).get('num_gpa')
            report_text = f'{report_text}\nГПА {num_gpa} - {w_time}'
            sum_time += w_time
        data = {
            'month': const.MONTHS_NAMES[str(prev_month.month)],
            'year': prev_month.year,
            'index_num': index_num + 1,
            'index_sum': index_sum,
            'report_text': report_text,
            'ks': ks_data['ks'],
            'sum_time': sum_time,
            'nav_is_on': nav_is_on,
            'report_not_empty': True,
            'report_is_empty': False
        }
    else:
        data = {
            'report_not_empty': False,
            'report_is_empty': True
        }
    return data


async def get_years(dialog_manager: DialogManager, **middleware_data):
    # context = dialog_manager.current_context()
    # station = context.dialog_data['station']
    years = operating_time.distinct('year')
    return {'years': years}


async def get_months(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    year = context.dialog_data['year']
    months = operating_time.distinct('month', {'year': int(year)})
    print(months)
    return {'months': [const.MONTHS_NAMES[str(m)] for m in months]}


# async def get_gpa(dialog_manager: DialogManager, **middleware_data):
#     context = dialog_manager.current_context()
#     shop = context.dialog_data['shop']
#     station = context.dialog_data['station']
#     queryset = gpa.find({'ks': station, 'num_shop': shop}).distinct('num_gpa')
#     return {'gpa': queryset}


# async def get_ao_info(dialog_manager: DialogManager, **middleware_data):
#     context = dialog_manager.current_context()
#     num_gpa = context.dialog_data['gpa']
#     station = context.dialog_data['station']
#     gpa_instance = gpa.find_one({'ks': station, 'num_gpa': num_gpa})
#     ao_count = emergency_stops.count_documents({'gpa_id': gpa_instance['_id']})
#     return {
#         'station': station,
#         'gpa_num': num_gpa,
#         'gpa_name': gpa_instance['name_gpa'],
#         'ao_count': ao_count,
#         'ao_not_null': True if ao_count > 0 else False
#     }


# async def get_users_info(dialog_manager: DialogManager, **middleware_data):
#     context = dialog_manager.current_context()
#     try:
#         users_info = context.dialog_data['resume_text']
#     except:
#         users_info = None
#     no_users_info = True if users_info is None else False
#     return {'users_info': users_info, 'no_users_info': no_users_info}
