from aiogram_dialog import DialogManager

from config.mongo_config import admins, paths
from config.telegram_config import MY_TELEGRAM_ID
import utils.constants as const


async def get_admins(dialog_manager: DialogManager, **middleware_data):
    queryset = list(admins.find({'user_id': {'$ne': int(MY_TELEGRAM_ID)}}))
    return {'admins': queryset}


async def get_single_admin(dialog_manager: DialogManager, **middleware_data):
    user_id = dialog_manager.event.from_user.id
    context = dialog_manager.current_context()
    admin_id = int(context.dialog_data['admin_id'])
    admin = admins.find_one({'user_id': admin_id})
    admin_info = {
        'username': admin['username'],
        'user_id': admin['user_id'],
        'owner': user_id == admin_id,
        'not_owner': user_id != admin_id,
        'sub_on': admin.get('sub', True),
        'sub_off': not admin.get('sub', True),
    }
    return admin_info


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
    return {'path_name': const.PATH_TYPE[path_type]}


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
        'path_name': const.PATH_TYPE[context.dialog_data['path_type']],
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
        'path_name': const.PATH_TYPE[context.dialog_data['path_type']],
        'num_stages': num_stages,
        'stages_info': stages_info,
    }
    return data
