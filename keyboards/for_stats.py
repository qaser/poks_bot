from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import utils.constants as const

def sort_kb(sort_param):
    keyboard = InlineKeyboardMarkup()
    if sort_param == 'ks':
        keyboard.add(
            InlineKeyboardButton(
                text=f'{const.SORT_EMOJI} по количеству',
                callback_data='sort_count'
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text=f'{const.SORT_EMOJI} по типу ГПА',
                callback_data='sort_gpa'
            )
        )
    else:
        keyboard.add(
            InlineKeyboardButton(
                text=f'{const.SORT_EMOJI} по станциям',
                callback_data='sort_ks'
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text=f'{const.UNDONE_EMOJI} Закрыть',
            callback_data='cancel'
        )
    )
    return keyboard
