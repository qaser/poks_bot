import datetime as dt

import aiohttp
from bson import ObjectId
from pytz import timezone
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager, StartMode

import utils.constants as const
from config.bot_config import bot
from config.mongo_config import gpa, paths, reqs
from config.pyrogram_config import app
from config.telegram_config import BOT_ID, EXPLOIT_GROUP_ID, MY_TELEGRAM_ID
from dialogs.for_request.states import Request

DATE_ERROR_MSG = (
    'Выбранная дата уже прошла.\n'
    'Пожалуйста, выберите другой рабочий день (начиная с текущего дня)'
)
TIME_ERROR_MSG = (
    'Выбранное время уже прошло или близко к текущему.\n'
    'Пожалуйста, выберите время на час позже текущего.\n'
    'Если ни одно время не подходит, то запланируйте пуск на следующий день.'
)


async def on_main_menu(callback, widget, manager: DialogManager):
    await manager.start(Request.select_station, mode=StartMode.RESET_STACK)


async def on_select_category(callback, widget, manager: DialogManager):
    category = widget.widget_id
    if category == 'paths':
        await manager.switch_to(Request.paths_info)
    elif category == 'new_request':
        await manager.switch_to(Request.select_station)
    elif category == 'archive_requests':
        await manager.switch_to(Request.select_sorting_requests)
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


async def is_holiday(target_date: dt.date) -> bool:
    """Проверяет, является ли дата праздничным днём в России"""
    year = target_date.year
    url = f"https://isdayoff.ru/api/getdata?year={year}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.text()
                    # Данные возвращаются в виде строки с кодами для каждого дня года
                    day_of_year = target_date.timetuple().tm_yday - 1
                    return data[day_of_year] == '1'  # '1' - праздник/выходной
    except Exception as e:
        print(f"Ошибка при проверке праздников: {e}")
    return False


async def on_select_date(callback, widget, manager: DialogManager, clicked_date):
    context = manager.current_context()
    today = dt.datetime.now().date()
    # Проверка на прошедшую дату
    if clicked_date < today:
        error_message = "❌ Нельзя выбрать прошедшую дату. Пожалуйста, выберите будущую дату."
        await callback.answer(error_message, show_alert=True)
        await manager.switch_to(Request.select_date)
        return
    # Проверка на выходные (суббота, воскресенье)
    if clicked_date.weekday() in (5, 6):
        error_message = "❌ Выбран выходной день (суббота/воскресенье). Пожалуйста, выберите рабочий день."
        await callback.answer(error_message, show_alert=True)
        await manager.switch_to(Request.select_date)
        return
    # Проверка на праздничный день
    if await is_holiday(clicked_date):
        error_message = "❌ Выбран праздничный день. Пожалуйста, выберите рабочий день."
        await callback.answer(error_message, show_alert=True)
        await manager.switch_to(Request.select_date)
        return
    # Если все проверки пройдены
    req_date = clicked_date.strftime('%d.%m.%Y')
    context.dialog_data.update(req_date=req_date)
    await manager.switch_to(Request.select_time)


async def on_select_time(callback, widget, manager: DialogManager, time: str):
    context = manager.current_context()
    today = dt.datetime.now().date()
    # Получаем выбранную дату из контекста
    req_date_str = context.dialog_data.get('req_date')
    try:
        req_date = dt.datetime.strptime(req_date_str, '%d.%m.%Y').date()
    except (ValueError, TypeError):
        req_date = today
    # Парсим выбранное время
    try:
        selected_time = dt.datetime.strptime(time, '%H:%M').time()
    except ValueError:
        await callback.answer("Некорректный формат времени", show_alert=True)
        return
    # Если выбранная дата - сегодня, проверяем время
    if req_date == today:
        now = dt.datetime.now()
        current_time_plus_hour = (now + dt.timedelta(hours=1)).time()
        if selected_time < current_time_plus_hour:
            await callback.answer(TIME_ERROR_MSG, show_alert=True)
            await manager.switch_to(Request.select_time)
            return
    # Если проверки пройдены, сохраняем время
    context.dialog_data['req_time'] = time
    await manager.switch_to(Request.input_info)


async def on_input_info(callback, widget, manager: DialogManager, request_text):
    context = manager.current_context()
    context.dialog_data.update(request_text=request_text)
    try:
        await callback.delete()
    except Exception as e:
        pass
    try:
        await callback.bot.delete_message(
            chat_id=callback.from_user.id,
            message_id=callback.message_id - 1
        )
    except Exception as e:
        pass
    await manager.switch_to(Request.request_confirm)


async def on_confirm(callback, widget, manager: DialogManager):
    context = manager.current_context()
    request_datetime = dt.datetime.strptime(f"{context.dialog_data['req_date']} {context.dialog_data['req_time']}", "%d.%m.%Y %H:%M")
    gpa_instance = gpa.find_one({'ks': context.dialog_data['station'], 'num_gpa': context.dialog_data['gpa']})
    path_type = get_path_type(gpa_instance)
    path_instance = paths.find_one({'path_type': path_type})
    current_stage = 1
    req_id = reqs.insert_one({
        'author_id': manager.event.from_user.id,
        'ks': context.dialog_data['station'],
        'num_gpa': context.dialog_data['gpa'],
        'gpa_id': gpa_instance['_id'],
        'datetime': dt.datetime.now(),
        'text': context.dialog_data['request_text'],
        'path_id': path_instance['_id'],
        'status': 'inwork',
        'current_stage': current_stage,
        'request_datetime': request_datetime,
        'notification_datetime': request_datetime + dt.timedelta(hours=3),
        'is_complete': False,
        'stages': {
            '1': {
                'status': 'pending',
                'datetime': dt.datetime.now(),
                'major_id': path_instance['stages']['1'],
            },
        }
    }).inserted_id
    await manager.switch_to(Request.request_finish)
    await send_request_to_major(req_id, current_stage)


async def on_selected_inwork_request(callback, widget, manager: DialogManager, req_id):
    context = manager.current_context()
    context.dialog_data.update(req_id=req_id)
    await manager.switch_to(Request.show_inwork_single_request)


async def on_select_sorting(callback, widget, manager: DialogManager):
    category = widget.widget_id
    if category == 'sort_date':
        await manager.switch_to(Request.date_sort_requests)
    elif category == 'sort_status':
        await manager.switch_to(Request.status_sort_requests)
    elif category == 'sort_ks':
        await manager.switch_to(Request.ks_sort_requests)


async def on_status_done(callback, widget, manager: DialogManager, status):
    context = manager.current_context()
    context.dialog_data.update(status=status, sorting_order='status')
    await manager.switch_to(Request.show_list_requests)


async def on_ks_done(callback, widget, manager: DialogManager, ks):
    context = manager.current_context()
    context.dialog_data.update(ks=ks, sorting_order='ks')
    await manager.switch_to(Request.show_list_requests)


async def on_date_done(callback, widget, manager: DialogManager, clicked_date):
    context = manager.current_context()
    context.dialog_data.update(date=clicked_date.strftime('%d.%m.%Y'), sorting_order='date')
    await manager.switch_to(Request.show_list_requests)


async def on_selected_request(callback, widget, manager: DialogManager, req_id):
    context = manager.current_context()
    context.dialog_data.update(req_id=req_id)
    await manager.switch_to(Request.show_single_request)


async def on_delete_req(callback, widget, manager: DialogManager):
    context = manager.current_context()
    req_id = context.dialog_data['req_id']
    reqs.delete_one({'_id': ObjectId(req_id)})
    await manager.switch_to(Request.show_list_requests)


def get_path_type(gpa_instance):
    type_gpa = gpa_instance['type_gpa']
    group_gpa = gpa_instance['group_gpa']
    if type_gpa == 'Стационарные' and group_gpa == 'ГТК-10-4':
        return 'Стационарные ГПА (ГТК-10-4)'
    elif type_gpa == 'Стационарные':
        return 'Стационарные ГПА'
    elif type_gpa == 'Авиационный привод':
        return 'ГПА с авиа. приводом'
    elif type_gpa == 'Судовой привод':
        return 'ГПА с судовым приводом'


async def send_request_to_major(req_id, current_stage):
    req = reqs.find_one({'_id': req_id})
    path_instance = paths.find_one({'_id': req['path_id']})
    gpa_instance = gpa.find_one({'_id': req['gpa_id']})
    author_name = (await bot.get_chat(req['author_id'])).full_name
    while current_stage <= path_instance['num_stages']:
        major_stage_id = path_instance['stages'][str(current_stage)]
        stages_text = await build_stages_text(req_id, path_instance, current_stage)
        request_text = await build_req_text(req, gpa_instance, stages_text, author_name, new_req=True)
        kb = InlineKeyboardBuilder()
        kb.button(text='🔴 Отклонить', callback_data=f'req_reject_{req_id}_{current_stage}')
        kb.button(text='🟢 Согласовать', callback_data=f'req_apply_{req_id}_{current_stage}')
        kb.adjust(2)
        try:
            await bot.send_message(major_stage_id, text=request_text, reply_markup=kb.as_markup())
            reqs.update_one({'_id': req_id}, {'$set': {
                f'stages.{current_stage}': {
                    'datetime': dt.datetime.now(),
                    'major_id': major_stage_id,
                    'status': 'inwork'
                },
                'current_stage': current_stage
            }})
            break
        except (TelegramForbiddenError, TelegramBadRequest):
            reqs.update_one({'_id': req_id}, {'$set': {
                f'stages.{current_stage}.status': 'pass',
                f'stages.{current_stage}.datetime': dt.datetime.now(),
                f'stages.{current_stage}.major_id': major_stage_id
            }})
            current_stage += 1
            req = reqs.find_one({'_id': req_id})
        except Exception:
            break
    else:
        # await send_notify(req_id, gpa_instance, path_instance, is_fallback=True, is_group=True)
        pass


async def build_req_text(req, gpa_instance, stages_text, author_name, new_req=False):
    tz = timezone(const.TIME_ZONE)
    request_text = (
        f"📅 Дата создания: {req['datetime'].astimezone(tz).strftime('%d.%m.%Y %H:%M')}\n"
        f"🏭 Станция: {req['ks']}\n"
        f"👤 Автор: {author_name}\n\n"
        f"<b>Информация о ГПА:</b>\n"
        f"Ст.№ ГПА: {gpa_instance['num_gpa']}\n"
        f"Наименование ГПА: {gpa_instance['name_gpa']}\n"
        f"Тип ГПА: {gpa_instance['type_gpa']}\n"
        f"Тип нагнетателя: {gpa_instance['cbn_type']}\n\n"
        f"<b>Планируемое время запуска:</b>\n{req['request_datetime'].strftime('%d.%m.%Y %H:%M')}\n\n"
        f"<b>Текст запроса:</b>\n<i>{req['text']}</i>\n\n"
        f"<b>Статус согласования:</b>\n{stages_text}\n"
    )
    request_text = f'<b>Новый запрос на пуск ГПА</b>\n{request_text}' if new_req else f'<b>Запрос на пуск ГПА</b>\n{request_text}'
    request_text = f'{request_text}Пожалуйста, согласуйте или отклоните запрос:' if new_req else request_text
    return request_text


async def build_stages_text(req_id, path_instance, current_stage):
    result = ''
    req = reqs.find_one({'_id': req_id})
    for stage_num in range(1, path_instance['num_stages'] + 1):
        stage_data = req['stages'].get(str(stage_num), {})
        status = stage_data.get('status', 'inwork' if stage_num == current_stage else 'pending')
        icon = {'apply': '🟢', 'reject': '🔴', 'pass': '⚫'}.get(status, '⚪')

        # Определяем имя ответственного
        if stage_num == current_stage and status not in ('inwork', 'pending'):
            # Для текущего этапа с завершенным статусом показываем ответственного
            try:
                major_name = (await bot.get_chat(stage_data['major_id'])).full_name if 'major_id' in stage_data else 'недоступен'
            except:
                major_name = 'недоступен'
        elif stage_num == current_stage:
            # Для текущего этапа в работе/ожидании
            major_name = 'текущий этап'
        else:
            # Для всех остальных этапов
            try:
                major_name = (await bot.get_chat(stage_data['major_id'])).full_name if 'major_id' in stage_data else 'ожидается'
            except:
                major_name = 'недоступен'
        tz = timezone(const.TIME_ZONE)
        date_str = stage_data.get('datetime', '').astimezone(tz).strftime('%d.%m.%Y %H:%M') if 'datetime' in stage_data else ""
        result += f"{icon} Этап {stage_num} - {major_name}" + (f" ({date_str})" if date_str else "") + "\n"

    return result


async def send_notify(req_id, gpa_instance, path, is_fallback=False, is_group=True, reason='', is_rejected=False):
    tz = timezone(const.TIME_ZONE)
    req = reqs.find_one({'_id': req_id})
    if not req:
        return
    author_name = (await bot.get_chat(req['author_id'])).full_name
    gpa_info = (
        f'<b>Ст.№ ГПА:</b> {gpa_instance["num_gpa"]}\n'
        f'<b>Наименование ГПА:</b> {gpa_instance["name_gpa"]}\n'
        f'<b>Тип ГПА:</b> {gpa_instance["type_gpa"]}\n'
        f'<b>Тип нагнетателя:</b> {gpa_instance["cbn_type"]}'
    )
    # Формируем заголовок в зависимости от получателя и статуса
    if is_group:
        if is_fallback:
            header = '⚠️ Получен запрос на согласование пуска ГПА, но адресаты временно не доступны\n\n'
        else:
            header = '✅ Запрос на пуск ГПА согласован\n\n'
    else:
        if is_rejected:
            header = f'🔴 Ваш запрос не согласован по причине:\n<i>{reason}</i>\n\n'
        else:
            header = '🟢 Ваш запрос согласован!\n\n'
    # Формируем информацию о стадиях согласования
    stages_text = ''
    if not is_fallback and not is_rejected:  # Показываем этапы для успешного согласования
        for stage_num in range(1, path['num_stages'] + 1):
            stage_data = req['stages'].get(str(stage_num), {})
            status = stage_data.get('status', 'pending')
            icon = ('🟢' if status == 'apply' else
                   '🔴' if status == 'reject' else
                   '⚫' if status == 'pass' else '⚪')
            major_name = 'ожидается'
            if 'major_id' in stage_data:
                try:
                    major_chat = await bot.get_chat(stage_data['major_id'])
                    major_name = major_chat.full_name
                except:
                    major_name = 'недоступен'
            date_str = stage_data.get('datetime', '').astimezone(tz).strftime('%d.%m.%Y %H:%M') if 'datetime' in stage_data else ""
            stages_text += f"{icon} Этап {stage_num} - {major_name}" + (f" ({date_str})" if date_str else "") + "\n"
    # Формируем основной текст сообщения
    request_text = (
        f"{header}"
        f"📅 Дата запроса: {req['datetime'].astimezone(tz).strftime('%d.%m.%Y %H:%M')}\n"
        f"🏭 Станция: {req['ks']}\n"
        f"👤 Автор: {author_name}\n\n"
        f"<u>Информация о ГПА:</u>\n{gpa_info}\n\n"
        f"<b>Текст запроса:</b>\n<i>{req['text']}</i>\n"
    )
    # Добавляем информацию о стадиях для успешного согласования
    if not is_fallback and not is_rejected and stages_text:
        request_text += f"\n<b>Этапы согласования:</b>\n{stages_text}\n"
    # Отправляем сообщение
    try:
        if is_group:
            await bot.send_message(
                chat_id=EXPLOIT_GROUP_ID,
                # message_thread_id=REQUEST_THREAD_ID,
                text=request_text
            )
        else:
            message_effect = '5104858069142078462' if is_fallback else '5046509860389126442'
            await bot.send_message(
                chat_id=req['author_id'],
                message_effect_id=message_effect,
                text=request_text
            )
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")
