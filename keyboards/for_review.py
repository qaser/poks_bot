from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import utils.constants as const


def directions_kb(dirs):
    keyboard = InlineKeyboardMarkup()
    for dir_code in dirs:
        keyboard.row(
            InlineKeyboardButton(
                text=const.DIRECTIONS_CODES.get(dir_code),
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


def ks_kb(ks_list, dir_code, level):
    keyboard = InlineKeyboardMarkup()
    for ks in ks_list:
        name, ks_id, count = ks
        keyboard.row(
            InlineKeyboardButton(
                text=f'{name} ({count})',
                callback_data=f'ks_{ks_id}_{dir_code}'
            )
        )
    keyboard.row(
        InlineKeyboardButton(
            text=f'{const.BACK_EMOJI} Назад',
            callback_data=f'back_{level}_{dir_code}'
        ),
        InlineKeyboardButton(
            text=f'{const.UNDONE_EMOJI} Выход',
            callback_data='cancel'
        )
    )
    return keyboard


def back_kb(dir_code, level):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            text=f'{const.BACK_EMOJI} Назад',
            callback_data=f'back_{level}_{dir_code}'
        ),
        InlineKeyboardButton(
            text=f'{const.UNDONE_EMOJI} Выход',
            callback_data='cancel'
        )
    )
    return keyboard


def get_drop_messages_kb(drop_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=f'{const.UNDONE_EMOJI} Выход',
            callback_data=f'drop_{drop_id}'
        )
    )
    return keyboard


def status_kb(pet_id, status_code):
    keyboard = InlineKeyboardMarkup(row_width=2)
    btns = []
    for status in const.PETITION_STATUS.keys():
        if status == status_code or status == 'create':
            continue
        _, btn_name, status_emoji = const.PETITION_STATUS[status]
        btn = InlineKeyboardButton(
            text=f'{status_emoji} {btn_name}',
            callback_data=f'status_{pet_id}_{status}_{status_code}'
        )
        btns.append(btn)
    keyboard.add(*btns)
    return keyboard
