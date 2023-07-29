from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import utils.constants as const


def directions_kb(dir_list):
    keyboard = InlineKeyboardMarkup()
    for dir in dir_list:
        dir_code, count = dir
        dir_name = const.DIRECTIONS_CODES.get(dir_code)
        keyboard.row(
            InlineKeyboardButton(
                text=f'{dir_name} ({count})',
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


def user_directions_kb(dir_list, ks):
    keyboard = InlineKeyboardMarkup()
    ks_id = const.KS.index(ks)
    for dir in dir_list:
        dir_code, count = dir
        dir_name = const.DIRECTIONS_CODES.get(dir_code)
        keyboard.row(
            InlineKeyboardButton(
                text=f'{dir_name} ({count})',
                callback_data=f'udir_{dir_code}_{ks_id}'
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


def ks_user_kb(ks_list):
    keyboard = InlineKeyboardMarkup()
    for ks_id in ks_list:
        name = const.KS[ks_id]
        keyboard.row(
            InlineKeyboardButton(
                text=name,
                callback_data=f'userks_{ks_id}'
            )
        )
    keyboard.add(
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


def status_kb(pet_id, status_code, job):
    keyboard = InlineKeyboardMarkup(row_width=2)
    btns = []
    if job == 'admin':
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
    else:
        for status in const.PETITION_STATUS.keys():
            if status == status_code or status in ['create', 'rework', 'inwork']:
                continue
            _, btn_name, status_emoji = const.PETITION_STATUS[status]
            btn = InlineKeyboardButton(
                text=f'{status_emoji} {btn_name}',
                callback_data=f'status_{pet_id}_{status}_{status_code}'
            )
            btns.append(btn)
        keyboard.add(*btns)
        if status_code == 'rework':
            keyboard.add(
                InlineKeyboardButton(
                    text=f'{const.EDIT_EMOJI} Редактировать запись',
                    callback_data=f'edit_{pet_id}_{status}_{status_code}'
                )
            )
        return keyboard
