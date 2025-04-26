from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from config.bot_config import bot
from config.mongo_config import emergency_stops, gpa, otkaz_msgs
from config.telegram_config import MY_TELEGRAM_ID, OTKAZ_GROUP_ID
from dialogs.for_request import windows
from dialogs.for_request.states import Request
from aiogram.enums import ChatType


router = Router()

dialog =  Dialog(
    windows.stations_window(),
    windows.shops_window(),
    windows.gpa_window(),
    windows.input_info_window(),
    windows.request_confirm_window(),
    windows.finish_window(),
)


@router.message(Command('request'), F.chat.type == ChatType.PRIVATE)
async def make_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    # print(message)
    await dialog_manager.start(Request.select_station, mode=StartMode.RESET_STACK)
