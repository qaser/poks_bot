import datetime as dt
from collections import Counter

from aiogram_dialog import DialogManager
from bson.objectid import ObjectId

from config.bot_config import bot
from config.mongo_config import admins, gpa, paths, reqs
from config.telegram_config import MY_TELEGRAM_ID
from dialogs.for_request.selected import build_req_text, build_stages_text
from utils.constants import KS, PATH_TYPE, REQUEST_STATUS


async def get_type_request(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    req_type = context.dialog_data['req_type']
    without_approval = True if req_type == 'without_approval' else False
    return {
        'without_approval': without_approval,
        'with_approval': not without_approval
    }


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


async def get_date_options(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    today = dt.datetime.now()
    tomorrow = today + dt.timedelta(days=1)
    type_req = context.dialog_data['req_type']
    calendar_on = True if type_req == 'with_approval' else False
    return {
        'calendar_on': calendar_on,
        'calendar_off': not calendar_on,
        'today': today.strftime('%d.%m.%Y'),
        'tomorrow': tomorrow.strftime('%d.%m.%Y'),
    }


async def get_request_info(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    num_gpa = context.dialog_data['gpa']
    station = context.dialog_data['station']
    req_type = context.dialog_data['req_type']
    gpa_instance = gpa.find_one({'ks': station, 'num_gpa': num_gpa})
    without_approval = True if req_type == 'without_approval' else False
    return {
        'station': station,
        'gpa_num': num_gpa,
        'gpa_name': gpa_instance['name_gpa'],
        'request_text': context.dialog_data['request_text'],
        'req_date': context.dialog_data['req_date'],
        'req_time': context.dialog_data['req_time'],
        'without_approval': without_approval,
        'with_approval': not without_approval
    }


async def get_inwork_requests(dialog_manager: DialogManager, **middleware_data):
    user_id = dialog_manager.event.from_user.id
    admin = admins.find_one({'user_id': user_id})
    is_admin = bool(admin)
    if is_admin:
        queryset = list(reqs.find({'status': 'inwork', 'req_type': 'with_approval'}))
    else:
        queryset = list(reqs.find({'status': 'inwork', 'author_id': user_id, 'req_type': 'with_approval'}))
    res = [
        {
            'name': f"#{q['req_num']} {q['ks']} - ГПА{gpa.find_one({'_id': q['gpa_id']})['num_gpa']} ({q['request_datetime'].strftime('%d.%m.%Y')})",
            'id': q['_id'],
        }
        for q in queryset
    ]
    is_empty = False if len(queryset) > 0 else True
    return {
        'is_empty': is_empty,
        'not_empty': not is_empty,
        'requests': res
    }


async def get_single_request(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    req_id = context.dialog_data['req_id']
    req = reqs.find_one({'_id': ObjectId(req_id)})
    current_stage = req['current_stage']
    path_instance = paths.find_one({'_id': req['path_id']})
    gpa_instance = gpa.find_one({'_id': req['gpa_id']})
    author_name = (await bot.get_chat(req['author_id'])).full_name
    stages_text = await build_stages_text(ObjectId(req_id), path_instance, current_stage)
    text = await build_req_text(req, gpa_instance, stages_text, author_name)
    return {
        'text': text,
        'has_files': True if req.get('files', {}) else False
    }


async def get_statuses(dialog_manager: DialogManager, **middleware_data):
    statuses = reqs.find({'req_type': 'with_approval'}).distinct('status')
    return {'statuses': [(status, REQUEST_STATUS[status]) for status in statuses]}


async def get_ks(dialog_manager: DialogManager, **middleware_data):
    ks = reqs.find({'req_type': 'with_approval'}).distinct('ks')
    return {'ks': ks}


async def get_requests(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    sorting_order = context.dialog_data['sorting_order']
    if sorting_order == 'ks':
        ks = context.dialog_data['ks']
        queryset = list(reqs.find({'ks': ks}).sort('$natural', -1).limit(24))
        # queryset = list(reqs.find({'ks': ks,'req_type': 'with_approval'}).sort('$natural', -1).limit(24))
        data = {'ks': ks, 'is_ks': True, 'not_empty': True}
    elif sorting_order == 'status':
        status = context.dialog_data['status']
        queryset = list(reqs.find({'status': status}).sort('$natural', -1).limit(24))
        # queryset = list(reqs.find({'status': status, 'req_type': 'with_approval'}).sort('$natural', -1).limit(24))
        data = {'status': REQUEST_STATUS[status], 'is_status': True, 'not_empty': True}
    elif sorting_order == 'date':
        req_date_str = context.dialog_data.get('date')
        req_date = dt.datetime.strptime(req_date_str, '%d.%m.%Y').date()
        queryset = list(reqs.find({
            '$expr': {
                '$eq': [
                    {'$dateToString': {'format': '%Y-%m-%d', 'date': '$request_datetime'}},
                    req_date.strftime('%Y-%m-%d')
                ]
            },
            # 'req_type': 'with_approval'
        }).sort('$natural', -1).limit(24))
        data = {'date': req_date_str, 'is_date': True}
        if len(queryset) == 0:
            data.update(is_empty=True)
        else:
            data.update(not_empty=True)
    res = [
        {
            'name': f"#{q['req_num']} {q['ks']} - ГПА{gpa.find_one({'_id': q['gpa_id']})['num_gpa']} ({q['request_datetime'].strftime('%d.%m.%Y')})",
            'id': q['_id'],
        }
        for q in queryset
    ]
    data.update(requests=res, sorting_order=sorting_order)
    return data


async def get_paths_info(dialog_manager: DialogManager, **middleware_data):
    queryset = list(paths.find({}))
    result = []
    # Проверяем, есть ли пути
    paths_empty = len(queryset) == 0
    paths_on = not paths_empty  # Противоположное значение
    if not paths_empty:
        for path in queryset:
            # Основная информация о пути
            path_text = f"Направление: <b>{path['path_type']}</b>\n"
            path_text += f"Количество этапов: {path['num_stages']}\n"
            # Информация о стадиях
            for stage_num, admin_id in path['stages'].items():
                admin = admins.find_one({'user_id': admin_id})
                admin_name = admin.get('username') if admin else 'Пользователь удалён'
                path_text += f'<u>Этап №{stage_num}</u> - {admin_name}\n'
            result.append(path_text)
        # Объединяем все пути через двойной перенос строки
        data = '\n'.join(result)
    else:
        data = "Нет доступных путей"  # Текст при отсутствии путей
    return {
        'paths_info': data,
        'paths_empty': paths_empty,
        'paths_on': paths_on
    }


async def get_path_name(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    path_type = context.dialog_data['path_type']
    return {'path_name': PATH_TYPE[path_type]}


async def get_majors_and_stages(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    num_stages = int(context.dialog_data['num_stages'])
    widget = dialog_manager.find('s_majors')
    majors = widget.get_checked()
    stages_info = ''
    for stage_num in range(1, num_stages + 1):
        major_name = ''
        if majors and (stage_num - 1) < len(majors):
            admin_id = majors[stage_num - 1]
            admin = admins.find_one({'user_id': int(admin_id)})
            major_name = admin.get('username')
        stages_info += f'<b>Этап {stage_num}:</b> {major_name}\n'
    data = {
        'path_name': PATH_TYPE[context.dialog_data['path_type']],
        'num_stages': num_stages,
        'stages_info': stages_info,
        'complete': len(majors) == num_stages,
        'majors': list(admins.find({'user_id': {'$ne': int(MY_TELEGRAM_ID)}}))
        # 'majors': list(admins.find({}))
    }
    return data


async def get_path_complete_info(dialog_manager: DialogManager, **middleware_data):
    context = dialog_manager.current_context()
    num_stages = int(context.dialog_data['num_stages'])
    majors = context.dialog_data['majors']
    stages_info = ''
    for stage_num in range(1, num_stages + 1):
        major_name = ''
        admin_id = majors[stage_num - 1]
        admin = admins.find_one({'user_id': int(admin_id)})
        major_name = admin.get('username')
        stages_info += f'<b>Этап {stage_num}:</b> {major_name}\n'
    data = {
        'path_name': PATH_TYPE[context.dialog_data['path_type']],
        'num_stages': num_stages,
        'stages_info': stages_info,
    }
    return data


async def get_users_info(dialog_manager: DialogManager, **middleware_data):
    user_id = dialog_manager.event.from_user.id
    admin = admins.find_one({'user_id': user_id})
    is_admin = bool(admin)
    return {'is_admin': is_admin, 'is_user': not is_admin}
