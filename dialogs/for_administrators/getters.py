from aiogram_dialog import DialogManager

from config.mongo_config import admins
from config.telegram_config import MY_TELEGRAM_ID


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
