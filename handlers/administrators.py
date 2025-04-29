from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from dialogs.for_administrators import windows
from dialogs.for_administrators.states import Admins

router = Router()

dialog =  Dialog(
    windows.select_admins_window(),
    windows.single_admin_window(),
    windows.confirm_delete_window(),
)


@router.message(Command('admins'))
async def admins_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    await dialog_manager.start(Admins.select_admin, mode=StartMode.RESET_STACK)
