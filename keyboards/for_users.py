from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import utils.constants as const


def ks_kb(ks_list):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for ks in ks_list:
        ks_index, num = ks
        name = const.KS[ks_index]
        keyboard.row(
            InlineKeyboardButton(
                text=f'{name} ({num})',
                callback_data=f'users_{ks_index}'
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text=f'{const.UNDONE_EMOJI} Выход',
            callback_data='cancel'
        )
    )
    return keyboard


def back_kb():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(
            text=f'{const.BACK_EMOJI} Назад',
            callback_data='users-back'
        )
    )
    return keyboard
