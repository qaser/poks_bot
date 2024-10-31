# from collections import Counter
# import datetime as dt

# from aiogram_dialog import DialogManager
# from bson.objectid import ObjectId
# from dateutil.relativedelta import relativedelta

# from config.mongo_config import admins, emergency_stops, gpa, users, operating_time
# from utils.constants import KS


# async def get_last_report(dialog_manager: DialogManager, **middleware_data):
#     # user_id = dialog_manager.event.from_user.id
#     context = dialog_manager.current_context()
#     date = dt.datetime.now()
#     prev_month = date - relativedelta(months=1)
#     pipeline = [
#         {
#             '$lookup': {
#                 'from': 'operating_time',
#                 'localField': '_id',
#                 'foreignField': 'gpa_id',
#                 'as': 'work_data'
#             }
#         },
#         {'$unwind': '$working_data'},
#         {'$match': {'work_data.year': prev_month.year, 'work_data.month': prev_month.month}},
#         # {'$group': {'_id': '$ks', 'gpa_ids': {'$push': {"$toString": "$_id"}}}},
#         {'$group': {'_id': '$ks', 'gpa_ids': {'$push': "$_id"}}},
#         {'$project': {'_id': 0, 'ks': '$_id', 'gpa_ids': 1}},
#         {'$setWindowFields': {'sortBy': {'ks': 1}, 'output': {'index': {'$documentNumber': {}}}}},
#     ]
#     queryset = list(gpa.aggregate(pipeline))
#     saved_index = context.dialog_data.get('index_num')
#     index_num = 0 if saved_index is None else saved_index
#     ks_count = len(queryset)
#     index_sum = len(queryset)
#     if index_sum > 0:
#         context.dialog_data.update(index_sum=index_sum)
#         context.dialog_data.update(index_num=index_num)
#         ks = queryset[index_num]
#         gpa_ids = ks['gpa_ids']
#         sum_time = 0
#         nav_is_on = True if index_sum > 1 else False
#         for gpa_id in gpa_ids:
#             w_time = operating_time.find_one({'gpa_id': gpa_id})['price']
#             amount_price = price * i['amount']
#             cart_price += amount_price
#         data = {
#             'cart_price': cart_price,
#             'pos_num': pos_num + 1,
#             'pos_sum': pos_sum,
#             'date': positions[pos_num]['datetime'].strftime('%d.%m.%Y'),
#             'product': prod['title'],
#             'size': prod['size'],
#             'color': positions[pos_num]['color'],
#             'amount': positions[pos_num]['amount'],
#             'price': prod['price'],
#             'full_price': positions[pos_num]['full_price'],
#             'nav_is_on': nav_is_on,
#             'cart_not_empty': True,
#             'cart_is_empty': False
#         }
#     else:
#         data = {
#             'cart_not_empty': False,
#             'cart_is_empty': True
#         }
#     return data


# async def get_shops(dialog_manager: DialogManager, **middleware_data):
#     context = dialog_manager.current_context()
#     station = context.dialog_data['station']
#     queryset = gpa.find({'ks': station}).distinct('num_shop')
#     return {'shops': queryset}


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
