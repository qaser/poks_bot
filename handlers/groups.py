from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from dialogs.for_groups import windows
from dialogs.for_groups.states import Groups



router = Router()

dialog =  Dialog(
    windows.stations_window(),
    windows.gpa_window(),
    windows.links_window(),
)


@router.message(Command('groups'))
async def operating_time_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    await dialog_manager.start(Groups.select_station, mode=StartMode.RESET_STACK)
