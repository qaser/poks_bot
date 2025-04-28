from collections import Counter

from aiogram_dialog import DialogManager
from bson.objectid import ObjectId

from config.mongo_config import admins, paths, gpa
from utils.constants import KS, PATH_TYPE
from config.telegram_config import MY_TELEGRAM_ID


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
        'req_date': context.dialog_data['req_date'],
        'req_time': context.dialog_data['req_time'],
    }


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
