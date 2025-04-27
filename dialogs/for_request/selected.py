import datetime as dt
import re
import asyncio

from aiogram_dialog import DialogManager, StartMode

import utils.constants as const
from config.bot_config import bot
from config.mongo_config import gpa, reqs, paths
from config.pyrogram_config import app
from config.telegram_config import BOT_ID, MY_TELEGRAM_ID, OTKAZ_GROUP_ID
from dialogs.for_request.states import Request
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def on_main_menu(callback, widget, manager: DialogManager):
    await manager.start(Request.select_station, mode=StartMode.RESET_STACK)


async def on_station_done(callback, widget, manager: DialogManager, station):
    context = manager.current_context()
    context.dialog_data.update(station=station)
    await manager.switch_to(Request.select_shop)


async def on_shop_done(callback, widget, manager: DialogManager, shop):
    context = manager.current_context()
    context.dialog_data.update(shop=shop)
    await manager.switch_to(Request.select_gpa)


async def on_gpa_done(callback, widget, manager: DialogManager, gpa_num):
    context = manager.current_context()
    context.dialog_data.update(gpa=gpa_num)
    await manager.switch_to(Request.input_info)


async def on_input_info(callback, widget, manager: DialogManager, request_text):
    context = manager.current_context()
    context.dialog_data.update(request_text=request_text)
    await manager.switch_to(Request.request_confirm)


async def on_confirm(callback, widget, manager: DialogManager):
    author_id = manager.event.from_user.id
    context = manager.current_context()
    num_gpa = context.dialog_data['gpa']
    station = context.dialog_data['station']
    gpa_instance = gpa.find_one({'ks': station, 'num_gpa': num_gpa})
    gpa_id = gpa_instance['_id']
    request_text = context.dialog_data['request_text']
    path_type = get_path_type(gpa_instance)
    path_instance = paths.find_one({'path_type': path_type})
    current_stage = 1
    req_id = reqs.insert_one(
        {
            'author_id': author_id,
            'ks': station,
            'gpa_id': gpa_id,
            'datetime': dt.datetime.now(),
            'text': request_text,
            'path_id': path_instance['_id'],
            'status': 'inwork',
            'current_stage': current_stage,
            'stages': {
                '1': {
                    'status': 'pending',
                    'datetime': dt.datetime.now(),
                    'major_id': path_instance['stages']['1'],
                },
            }
        }
    ).inserted_id
    await manager.switch_to(Request.request_finish)
    await send_request_to_major(req_id, current_stage)


async def send_request_to_major(req_id, current_stage):
    req = reqs.find_one({'_id': req_id})
    path_instance = paths.find_one({'_id': req['path_id']})
    gpa_instance = gpa.find_one({'_id': req['gpa_id']})
    num_stages = path_instance['num_stages']
    stages = path_instance['stages']
    # Получаем информацию об авторе
    author = await bot.get_chat(req['author_id'])
    author_name = author.full_name
    # Формируем данные о ГПА
    iskra_comp = 'Да' if gpa_instance.get('iskra_comp', False) else 'Нет'
    gpa_info = (
        f'<b>Ст.№ ГПА:</b> {gpa_instance["num_gpa"]}\n'
        f'<b>Наименование ГПА:</b> {gpa_instance["name_gpa"]}\n'
        f'<b>Тип ГПА:</b> {gpa_instance["type_gpa"]}\n'
        f'<b>Тип нагнетателя:</b> {gpa_instance["cbn_type"]}\n'
        f'<b>Корпус "Искра":</b> {iskra_comp}\n'
        f'<b>Количество АО (ВНО):</b> {len(gpa_instance["ao"])}'
    )
    while current_stage <= num_stages:
        stages_text = ""
        for stage_num in range(1, num_stages + 1):
            stage_data = req['stages'].get(str(stage_num), {})
            status = stage_data.get('status', 'inwork' if stage_num == current_stage else 'pending')
            icon = ('🟢' if status == 'apply' else
                   '🔴' if status == 'reject' else
                   '⚫' if status == 'pass' else '⚪')
            major_name = "ожидается"
            if 'major_id' in stage_data:
                try:
                    major_chat = await bot.get_chat(stage_data['major_id'])
                    major_name = major_chat.full_name
                except:
                    major_name = "недоступен"
            date_str = stage_data.get('datetime', '').strftime('%d.%m.%Y %H:%M') if 'datetime' in stage_data else ""
            stages_text += f"{icon} Этап {stage_num} - {major_name}" + (f" ({date_str})" if date_str else "") + "\n"
        request_text = (
            f"<b>Новый запрос на пуск ГПА</b>\n\n"
            f"📅 Дата создания: {req['datetime'].strftime('%d.%m.%Y %H:%M')}\n"
            f'👤 Автор: {author_name}\n'
            f"🏭 Станция: {req['ks']}\n\n"
            f'<u>Информация о ГПА:</u>\n{gpa_info}\n\n'
            f"<b>Статус согласования:</b>\n{stages_text}\n"
            f"<b>Текст запроса:</b>\n<i>{req['text']}</i>\n\n"
            'Пожалуйста, согласуйте или отклоните запрос:'
        )
        major_stage_id = stages[str(current_stage)]
        kb = InlineKeyboardBuilder()
        kb.button(text='🔴 Отклонить', callback_data=f'req_reject_{req_id}_{current_stage}')
        kb.button(text='🟢 Согласовать', callback_data=f'req_apply_{req_id}_{current_stage}')
        kb.adjust(2)
        try:
            await bot.send_message(
                major_stage_id,
                text=request_text,
                reply_markup=kb.as_markup(),
            )
            # Обновляем БД после успешной отправки
            reqs.update_one(
                {'_id': req_id},
                {'$set': {
                    f'stages.{current_stage}': {
                        'datetime': dt.datetime.now(),
                        'major_id': major_stage_id,
                        'status': 'inwork'
                    },
                    'current_stage': current_stage
                }}
            )
            break
        except (TelegramForbiddenError, TelegramBadRequest):
            # Обновляем статус как "пропущен" перед переходом к следующему
            reqs.update_one(
                {'_id': req_id},
                {'$set': {
                    f'stages.{current_stage}.status': 'pass',
                    f'stages.{current_stage}.datetime': dt.datetime.now(),
                    f'stages.{current_stage}.major_id': major_stage_id
                }}
            )
            current_stage += 1
            # Обновляем запрос из БД для актуальных данных
            req = reqs.find_one({'_id': req_id})
        except Exception as e:
            print(e)
            break
    else:
        print(f"Запрос {req_id} не доставлен ни одному согласующему")


def get_path_type(gpa_instance):
    type_gpa = gpa_instance['type_gpa']
    group_gpa = gpa_instance['group_gpa']
    if type_gpa == 'Стационарные' and group_gpa == 'ГТК-10-4':
        path_type = 'Стационарные ГПА (ГТК-10-4)'
    elif type_gpa == 'Стационарные':
        path_type = 'Стационарные ГПА'
    elif type_gpa == 'Авиационный привод':
        path_type = 'ГПА с авиа. приводом'
    elif type_gpa == 'Судовой привод':
        path_type = 'ГПА с судовым приводом'
    return path_type
