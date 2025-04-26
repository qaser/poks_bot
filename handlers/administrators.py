from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

import utils.constants as const
from config.bot_config import bot
from config.telegram_config import MY_TELEGRAM_ID
from dialogs.for_administrators import windows
from dialogs.for_administrators.states import Admins


router = Router()

dialog =  Dialog(
    windows.select_category_window(),
    windows.select_admins_window(),
    windows.single_admin_window(),
    windows.confirm_delete_window(),
    windows.paths_info_window(),  # 4 кнопки с типами путей
    windows.select_num_stage(),
    windows.select_majors_window(),
    windows.confirm_path_window(),
    windows.complete_path_window(),
)


@router.message(Command('admins'))
async def admins_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    await dialog_manager.start(Admins.select_category, mode=StartMode.RESET_STACK)
