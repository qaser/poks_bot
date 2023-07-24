from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import utils.constants as const

def directions_kb():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btns = []
    for dir_code, dir_name in const.DIRECTIONS_CODES.items():
        btn = InlineKeyboardButton(
            text=dir_name,
            callback_data=f'pet_{dir_code}'
        )
        btns.append(btn)
    keyboard.add(*btns)
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
