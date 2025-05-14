import datetime as dt
import imaplib
import os

from aiogram.exceptions import AiogramError
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pytz import timezone
from collections import defaultdict

import utils.constants as const
from config.bot_config import bot
from config.mail_config import (ADMIN_EMAIL, IMAP_MAIL_SERVER, MAIL_LOGIN,
                                MAIL_PASS)
from config.mongo_config import groups, msgs, reqs, users, gpa
from config.telegram_config import (EXPLOIT_GROUP_ID, MY_TELEGRAM_ID,
                                    SPCH_THREAD_ID)
from utils.backup_db import send_dbs_mail
from utils.get_mail import get_letters

SPCH_TIME_WORK_MSG = ('В срок до 12:00 текущего дня прошу выложить фактическую наработку за прошедший месяц.\n\n'
                      'Пример:\n\nКС «Примерная»:\nГПА 12 - 720\nГПА 24 - 9\n\n'
                      'Соблюдайте форму примера для корректной автоматической обработки данных')


async def clear_msgs():
    queryset = list(msgs.find({}))
    for msg in queryset:
        try:
            await bot.delete_message(chat_id=int(msg['chat_id']), message_id=msg['msg_id'])
        except AiogramError:
            pass
        msgs.delete_one({'chat_id': msg['chat_id'], 'message_id': msg['msg_id']})


async def send_remainder():
    queryset = list(groups.find({'sub_banned': 'false'}))
    num_groups = groups.count_documents({'sub_banned': 'false'})
    await bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text=f'Всего отслеживается групп: {num_groups}'
    )
    count_groups = 0
    for group in queryset:
        id = group.get('_id')
        name = group.get('group_name')
        try:
            msg = await bot.send_message(chat_id=int(id), text=const.GROUP_REMAINDER)
            msgs.insert_one({'msg_id': msg.message_id, 'chat_id': id})
            await bot.send_message(
                chat_id=MY_TELEGRAM_ID,
                text=f'Группе "{name}" отправлено напоминание'
            )
            count_groups = count_groups + 1
        except AiogramError:
            pass
    await bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text=('Задача рассылки уведомлений завершена.\n'
              f'Всего обработано групп: {count_groups}')
    )


async def send_task_users_reminder():
    queryset = users.distinct('user_id')
    for user_id in queryset:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=const.TASK_REMINDER,
            )
        except:
            pass


async def check_mailbox():
    mail_pass = MAIL_PASS
    username = MAIL_LOGIN
    imap_server = IMAP_MAIL_SERVER
    imap = imaplib.IMAP4_SSL(imap_server)
    status, res = imap.login(username, mail_pass)
    if status == 'OK' and imap:
        await get_letters(imap)


async def send_backups():
    cur_date = dt.datetime.now().strftime('%d-%m-%y')
    # backup_dir = f'C:\Dev\poks_bot\\var\\backups\mongobackups\{cur_date}'
    backup_dir = f'../../../var/backups/mongobackups/{cur_date}'
    for db_name in os.listdir(backup_dir):
        if db_name in ['poks_bot_db', 'tehnika_bot_db', 'quiz_db']:
            # backup_path = f'{backup_dir}\{db_name}'
            backup_path = f'{backup_dir}/{db_name}'
            emails = [ADMIN_EMAIL]
            await send_dbs_mail(emails, db_name, backup_path)


async def send_work_time_reminder():
    await bot.send_message(
        chat_id=EXPLOIT_GROUP_ID,
        text=SPCH_TIME_WORK_MSG,
        message_thread_id=SPCH_THREAD_ID
    )


async def find_overdue_requests():
    tz = timezone(const.TIME_ZONE)
    now = dt.datetime.now(tz)
    now_plus_5h = now + dt.timedelta(hours=5)
    res = list(reqs.find({
        'status': 'approved',
        'is_complete': False,
        'notification_datetime': {'$lt': now_plus_5h}
    }))
    for req in res:
        prime_date = req['datetime'].astimezone(tz).strftime('%d.%m.%Y %H:%M')
        req_date = req['request_datetime'].astimezone(tz).strftime('%d.%m.%Y %H:%M')
        gpa_instance = gpa.find_one({'_id': req['gpa_id']})
        msg_text=(
            f'Ваш запрос от {prime_date} на пуск ГПА №{gpa_instance["num_gpa"]} ({req["ks"]}) '
            f'был согласован. Согласованное время запуска <u>{req_date}</u> со временем, отведенным на пуск '
            'прошло.\nЕсли запуск ГПА завершён успешно нажмите кнопку <b>"Пуск завершён"</b>.\n'
            'Если во время запуска возникли проблемы нажмите <b>"Пуск не завершён"</b>,'
            'при этом необходимо будет указать причину неудачного запуска.'
        )
        kb = InlineKeyboardBuilder()
        kb.button(text='🔴 Пуск не завершён', callback_data=f'launch_fail_{req["_id"]}')
        kb.button(text='🟢 Пуск завершён', callback_data=f'launch_success_{req["_id"]}')
        kb.adjust(1)
        try:
            await bot.send_message(
                chat_id=req['author_id'],
                text=msg_text,
                reply_markup=kb.as_markup()
            )
        except Exception as err:
            await bot.send_message(
                chat_id=MY_TELEGRAM_ID,
                text='🔴 Не отправлено сообщение с кнопками подтверждения пуска'
            )


async def send_morning_report():
    today = dt.datetime.now().date()
    # Фильтр для поиска актуальных заявок на сегодня
    req_filter = {
        '$expr': {
            '$eq': [
                {'$dateToString': {'format': '%Y-%m-%d', 'date': '$request_datetime'}},
                today.strftime('%Y-%m-%d')
            ]
        },
        'status': 'approved',
        'is_complete': False,
    }
    # Получаем все заявки на сегодня
    queryset = list(reqs.find(req_filter).sort('request_datetime', 1))
    # Группируем заявки по типам ГПА
    gpa_types = defaultdict(list)
    for req in queryset:
        gpa_data = gpa.find_one({'_id': req['gpa_id']})
        if not gpa_data:
            continue
        # Определяем тип ГПА с учетом особого случая для ГТК-10-4
        if gpa_data['type_gpa'] == 'Стационарные' and gpa_data.get('group_gpa') == 'ГТК-10-4':
            gpa_type = 'Стационарные ГПА (ГТК-10-4)'
        elif gpa_data['type_gpa'] == 'Стационарные':
            gpa_type = 'Стационарные ГПА'
        elif gpa_data['type_gpa'] == 'Авиационный привод':
            gpa_type = 'ГПА с авиа. приводом'
        elif gpa_data['type_gpa'] == 'Судовой привод':
            gpa_type = 'ГПА с судовым приводом'
        else:
            gpa_type = gpa_data['type_gpa']

        # Формируем строку для отчета
        time_str = req['request_datetime'].strftime('%H:%M')
        report_line = f"{req['ks']} ГПА{gpa_data['num_gpa']} - {time_str}"
        gpa_types[gpa_type].append(report_line)

    # Формируем итоговый отчет
    report_lines = []

    # Порядок вывода типов ГПА в отчете
    type_order = [
        'ГПА с авиа. приводом',
        'ГПА с судовым приводом',
        'Стационарные ГПА',
        'Стационарные ГПА (ГТК-10-4)'
    ]
    for gpa_type in type_order:
        if gpa_type in gpa_types:
            report_lines.append(f"<b>{gpa_type}</b>:")
            report_lines.extend(gpa_types[gpa_type])
        else:
            report_lines.append(f"<b>{gpa_type}</b>: на сегодня заявок нет\n")
    # Объединяем все строки отчета
    report_text = "\n".join(report_lines)
    # Добавляем заголовок с текущей датой
    full_report = f"<u>Отчет по запланированным пускам ГПА на {today.strftime('%d.%m.%Y')}</u>\n{report_text}"
    await bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text=full_report,
    )


async def send_evening_report():
    today = dt.datetime.now().date()
    # Фильтр для поиска всех одобренных заявок на сегодня
    req_filter = {
        '$expr': {
            '$eq': [
                {'$dateToString': {'format': '%Y-%m-%d', 'date': '$request_datetime'}},
                today.strftime('%Y-%m-%d')
            ]
        },
        'status': 'approved',
    }
    # Получаем все заявки на сегодня
    queryset = list(reqs.find(req_filter).sort('request_datetime', 1))
    # Группируем заявки по типам ГПА
    gpa_types = defaultdict(list)
    for req in queryset:
        gpa_data = gpa.find_one({'_id': req['gpa_id']})
        if not gpa_data:
            continue
        # Определяем тип ГПА
        if gpa_data['type_gpa'] == 'Стационарные' and gpa_data.get('group_gpa') == 'ГТК-10-4':
            gpa_type = 'Стационарные ГПА (ГТК-10-4)'
        elif gpa_data['type_gpa'] == 'Стационарные':
            gpa_type = 'Стационарные ГПА'
        elif gpa_data['type_gpa'] == 'Авиационный привод':
            gpa_type = 'ГПА с авиа. приводом'
        elif gpa_data['type_gpa'] == 'Судовой привод':
            gpa_type = 'ГПА с судовым приводом'
        else:
            gpa_type = gpa_data['type_gpa']
        # Определяем статус пуска
        if req.get('is_fail') is True:
            reason = req.get('fail_reason', 'без указания причины')
            status = "🟥"
            status_text = f" ({reason})"
        elif req.get('is_complete') is True:
            status = "🟩"
            status_text = ""
        else:
            status = "⬜"
            status_text = " (не завершён)"
        # Формируем строку для отчета
        time_str = req['request_datetime'].strftime('%H:%M')
        report_line = f"{status} {req['ks']} ГПА{gpa_data['num_gpa']} - {time_str}{status_text}"
        gpa_types[gpa_type].append(report_line)
    # Формируем итоговый отчет
    report_lines = []
    # Порядок вывода типов ГПА в отчете
    type_order = [
        'ГПА с авиа. приводом',
        'ГПА с судовым приводом',
        'Стационарные ГПА',
        'Стационарные ГПА (ГТК-10-4)'
    ]
    for gpa_type in type_order:
        if gpa_type in gpa_types:
            report_lines.append(f"<b>{gpa_type}</b>:")
            report_lines.extend(gpa_types[gpa_type])
            report_lines.append("")  # Пустая строка между группами
        else:
            report_lines.append(f"<b>{gpa_type}</b>: заявок не было\n")
    # Объединяем все строки отчета
    report_text = "\n".join(report_lines)
    # Добавляем заголовок с текущей датой
    full_report = (
        f"<u>Отчет по пускам ГПА за {today.strftime('%d.%m.%Y')}</u>\n"
        f"{report_text}"
    )
    await bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text=full_report,
    )
