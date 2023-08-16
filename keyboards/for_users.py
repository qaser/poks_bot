from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import utils.constants as const


def ks_kb(ks_list):
    keyboard = InlineKeyboardMarkup(row_width=2)
    btns = []
    for ks in ks_list:
        ks_index, num = ks
        name = const.KS[ks_index]
        btn = InlineKeyboardButton(
            text=f'{name} ({num})',
            callback_data=f'users_{ks_index}'
        )
        btns.append(btn)
    keyboard.add(*btns)
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
