from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
            callback_data=f'new_cancel_none_{msg_id}'
        ),
        InlineKeyboardButton(
            text=f'{const.DONE_EMOJI} Да',
            callback_data=f'new_send_{dir}_{msg_id}'
        )
    )
    return keyboard


def upload_choose_kb(dir, msg_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=f'{const.DOC_EMOJI} Прикрепить файл',
            callback_data=f'upload'
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=f'{const.SEND_EMOJI} Отправить без файла',
            callback_data=f'new_send_{dir}_{msg_id}'
        )
    )
    return keyboard


def status_kb(pet_id, status_code, num_docs):
    keyboard = InlineKeyboardMarkup()
    btn_rework = InlineKeyboardButton(
        text=f'{const.REWORK_EMOJI} На доработку',
        callback_data=f'status_{pet_id}_rework_{status_code}'
    )
    btn_inwork = InlineKeyboardButton(
        text=f'{const.INWORK_EMOJI} В работу',
        callback_data=f'status_{pet_id}_inwork_{status_code}'
    )
    if num_docs > 0:
        keyboard.add(
            InlineKeyboardButton(
                text=f'{const.DOC_EMOJI} Посмотреть документы',
                callback_data=f'docs_{pet_id}'
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text=f'{const.SEND_EMOJI} Отправить ответ',
            callback_data=f'answer_{pet_id}'
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=f'{const.GROUP_EMOJI} Открыть чат',
            callback_data=f'group_{pet_id}'
        )
    )
    keyboard.row(btn_rework, btn_inwork)
    return keyboard


def edit_kb(pet_id):
    keyboard = InlineKeyboardMarkup()
    btn_delete = InlineKeyboardButton(
        text=f'{const.DELETE_EMOJI} Удалить',
        callback_data=f'status_{pet_id}_delete_rework'
    )
    btn_edit = InlineKeyboardButton(
        text=f'{const.EDIT_EMOJI} Редактировать',
        callback_data=f'edit_{pet_id}'
    )
    keyboard.row(btn_delete, btn_edit)
    return keyboard


def edit_send_kb(pet_id):
    keyboard = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(
        text=f'{const.SEND_EMOJI} Отправить',
        callback_data=f'status_{pet_id}_create_rework'
    )
    keyboard.add(btn)
    return keyboard


def ks_user_kb(ks_list):
    keyboard = InlineKeyboardMarkup()
    for ks_id in ks_list:
        name = const.KS[ks_id]
        keyboard.row(
            InlineKeyboardButton(
                text=name,
                callback_data=f'task-ks_{ks_id}'
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text=f'{const.UNDONE_EMOJI} Выход',
            callback_data='cancel'
        )
    )
    return keyboard


def get_upload_kb():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=f'{const.UNDONE_EMOJI} Отмена',
            callback_data='cancel'
        )
    )
    return keyboard


def full_status_kb(pet_id, status_code, num_docs, is_admin):
    keyboard = InlineKeyboardMarkup(row_width=2)
    btns = []
    status_list = const.PETITION_STATUS.keys() if is_admin else ['delete', 'finish']
    for status in status_list:
        if status == status_code or status == 'create':
            continue
        _, btn_name, status_emoji = const.PETITION_STATUS[status]
        btn = InlineKeyboardButton(
            text=f'{status_emoji} {btn_name}',
            callback_data=f'status_{pet_id}_{status}_{status_code}'
        )
        btns.append(btn)
    if num_docs > 0:
        keyboard.add(
            InlineKeyboardButton(
                text=f'{const.DOC_EMOJI} Посмотреть документы',
                callback_data=f'docs_{pet_id}'
            )
        )
    keyboard.add(*btns)
    return keyboard


def answer_kb(pet_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=f'{const.SEND_EMOJI} Отправить ответ',
            callback_data=f'answer_{pet_id}'
        )
    )
    return keyboard
