from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from dialogs.for_edit import windows
from dialogs.for_edit.states import Edit



router = Router()

dialog =  Dialog(
    windows.groups_window(),
    windows.confirm_window(),
    windows.finish_window(),
)


@router.message(Command('edit'))
async def operating_time_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    await dialog_manager.start(Edit.select_group, mode=StartMode.RESET_STACK)
