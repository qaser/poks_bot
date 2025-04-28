import datetime as dt
import re
import asyncio

from aiogram_dialog import DialogManager, StartMode

import utils.constants as const
from config.bot_config import bot
from config.mongo_config import gpa, reqs, paths
from config.pyrogram_config import app
from config.telegram_config import BOT_ID, MY_TELEGRAM_ID, EXPLOIT_GROUP_ID
from dialogs.for_request.states import Request
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder


ERROR_MSG = 'Можно выбрать дату начиная с завтрашнего дня и только рабочий день (с понедельника по пятницу)'


async def on_main_menu(callback, widget, manager: DialogManager):
    await manager.start(Request.select_station, mode=StartMode.RESET_STACK)


async def on_select_category(callback, widget, manager: DialogManager):
    category = widget.widget_id
    if category == 'paths':
        await manager.switch_to(Request.paths_info)
    elif category == 'new_request':
        await manager.switch_to(Request.select_station)
    elif category == 'my_requests':
        await manager.switch_to(Request.show_requests)
    elif category == 'inwork_requests':
        await manager.switch_to(Request.inwork_requests)


async def on_path_selected(callback, widget, manager: DialogManager):
    context = manager.current_context()
    _, _, path_type = widget.widget_id.split('_')
    context.dialog_data.update(path_type=path_type)
    await manager.switch_to(Request.select_num_stages)



async def on_num_stages_selected(callback, widget, manager: DialogManager):
    context = manager.current_context()
    _, _, num_stages = widget.widget_id.split('_')
    context.dialog_data.update(num_stages=num_stages)
    await manager.switch_to(Request.select_majors)


async def back_and_erase_widget_click(callbac, button, manager: DialogManager):
    widget = manager.find('s_majors')
    await widget.reset_checked()
    await manager.back()


async def on_majors_done(callback, widget, manager: DialogManager):
    context = manager.current_context()
    widget = manager.find('s_majors')
    context.dialog_data.update(majors=widget.get_checked())
    await manager.switch_to(Request.path_confirm)


async def path_save(callback, widget, manager: DialogManager):
    context = manager.current_context()
    num_stages = int(context.dialog_data['num_stages'])
    majors = context.dialog_data['majors']
    path_name = const.PATH_TYPE[context.dialog_data['path_type']]
    stages = {}
    for stage_num in range(1, num_stages + 1):
        stages[str(stage_num)] = int(majors[stage_num - 1])
    paths.update_one(
        {'path_type': path_name},
        {'$set': {'num_stages': num_stages, 'stages': stages}},
        upsert=True
    )
    widget = manager.find('s_majors')
    await widget.reset_checked()
    await manager.switch_to(Request.path_complete)


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
    await manager.switch_to(Request.select_date)


async def on_select_date(callback, widget, manager: DialogManager, clicked_date):
    context = manager.current_context()
    today = dt.datetime.now().date()
    # Объединенная проверка на прошедшую дату или выходной день
    if clicked_date <= today or clicked_date.weekday() in (5, 6):
        error_message = ERROR_MSG
        await callback.answer(error_message, show_alert=True)
        await manager.switch_to(Request.select_date)
        return
    req_date = clicked_date.strftime('%d.%m.%Y')
    context.dialog_data.update(req_date=req_date)
    await manager.switch_to(Request.select_time)


async def on_select_time(callback, widget, manager: DialogManager, time: str):
    context = manager.current_context()
    context.dialog_data['req_time'] = time
    await manager.switch_to(Request.input_info)


async def on_input_info(callback, widget, manager: DialogManager, request_text):
    context = manager.current_context()
    context.dialog_data.update(request_text=request_text)
    await manager.switch_to(Request.request_confirm)


async def on_confirm(callback, widget, manager: DialogManager):
    author_id = manager.event.from_user.id
    context = manager.current_context()
    num_gpa = context.dialog_data['gpa']
    req_date = context.dialog_data['req_date']
    req_time = context.dialog_data['req_time']
    request_datetime = dt.datetime.strptime(f"{req_date} {req_time}", "%d.%m.%Y %H:%M")
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
            'request_datetime': request_datetime,
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
    # await send_request_to_major(req_id, current_stage)


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
    gpa_info = (
        f'Ст.№ ГПА: {gpa_instance["num_gpa"]}\n'
        f'Наименование ГПА: {gpa_instance["name_gpa"]}\n'
        f'Тип ГПА: {gpa_instance["type_gpa"]}\n'
        f'Тип нагнетателя: {gpa_instance["cbn_type"]}'
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
            f"<b>Новый запрос на пуск ГПА</b>\n"
            f"📅 Дата создания: {req['datetime'].strftime('%d.%m.%Y %H:%M')}\n"
            f'👤 Автор: {author_name}\n'
            f"🏭 Станция: {req['ks']}\n\n"
            f'<b>Информация о ГПА:</b>\n{gpa_info}\n\n'
            f"<b>Планируемое время запуска:</b>\n{req['request_datetime'].strftime('%d.%m.%Y %H:%M')}\n\n"
            f"<b>Текст запроса:</b>\n<i>{req['text']}</i>\n\n"
            f"<b>Статус согласования:</b>\n{stages_text}\n"
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
            break
    else:
        request_text = (
            f"<b>Новый запрос на пуск ГПА</b>\n\n"
            f"📅 Дата создания: {req['datetime'].strftime('%d.%m.%Y %H:%M')}\n"
            f'👤 Автор: {author_name}\n'
            f"🏭 Станция: {req['ks']}\n\n"
            f'<u>Информация о ГПА:</u>\n{gpa_info}\n\n'
            f"<b>Текст запроса:</b>\n<i>{req['text']}</i>\n\n"
        )
        await bot.send_message(
            chat_id=EXPLOIT_GROUP_ID,
            text=request_text,
            # message_thread_id=SPCH_THREAD_ID
        )


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
