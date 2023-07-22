from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import utils.constants as const

def directions_kb():
    keyboard = InlineKeyboardMarkup()
    for dir_code, dir_name in const.DIRECTIONS_CODES.items():
        keyboard.row(
            InlineKeyboardButton(
                text=dir_name,
                callback_data=f'dir_{dir_code}'
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text=f'{const.UNDONE_EMOJI} Отмена',
            callback_data='cancel'
        )
    )
    return keyboard


def cancel_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=f'{const.UNDONE_EMOJI} Отмена',
            callback_data='cancel'
        )
    )
    return keyboard


def send_kb(dir, msg_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            text=f'{const.UNDONE_EMOJI} Нет',
            callback_data=f'ask_cancel_none_{msg_id}'
        ),
        InlineKeyboardButton(
            text=f'{const.DONE_EMOJI} Да',
            callback_data=f'ask_send_{dir}_{msg_id}'
        )
    )
    return keyboard
