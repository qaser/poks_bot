import asyncio
import datetime as dt

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import Dialog, DialogManager, StartMode
from bson import ObjectId
from pyrogram.types import ChatPermissions
from pytz import timezone

import utils.constants as const
from config.bot_config import bot
from config.mongo_config import (admins, buffer, emergency_stops, gpa, groups,
                                 paths, reqs)
from config.pyrogram_config import app
from config.telegram_config import BOT_ID, MY_TELEGRAM_ID, OTKAZ_GROUP_ID
from dialogs.for_ao.selected import add_admin_to_group, send_chat_links
from dialogs.for_request import windows
from dialogs.for_request.selected import (send_notify, send_request_to_major,
                                          show_req_files)
from dialogs.for_request.states import Request
from scheduler.scheduler_funcs import send_evening_report, send_morning_report
from utils.utils import report_error

router = Router()

dialog =  Dialog(
    windows.select_category_window(),

    windows.select_type_request_window(),  # выбор типа запроса (без согласования или с согласованием)
    windows.stations_window(),
    windows.shops_window(),
    windows.gpa_window(),

    windows.select_epb_window(),
    windows.input_epb_file_window(),

    windows.date_window(),
    windows.time_window(),

    windows.select_resource_window(),
    windows.input_logbook_file_window(),
    windows.select_resource_act_window(),
    windows.input_resource_act_file_window(),  # каждый 2-ой запрос
    windows.input_out_of_resource_reason_window(),

    windows.select_protocol_window(),
    windows.input_protocol_file_window(),  # каждый 4-ой запрос

    windows.select_card_window(),
    windows.input_card_file_window(),  # каждый 6-ой запрос

    windows.show_reject_window(),
    windows.input_info_window(),

    windows.select_priority_gpa_window(),
    windows.select_priority_criteria_window(),
    windows.input_priority_file_window(),

    windows.request_confirm_window(),
    windows.finish_window(),

    windows.inwork_requests_window(),
    windows.show_inwork_single_request_window(),

    windows.select_sorting_requests_window(),
    windows.date_sort_requests_window(),
    windows.status_sort_requests_window(),
    windows.ks_sort_requests_window(),
    windows.type_sort_requests_window(),
    windows.show_list_requests_window(),
    windows.show_single_request_window(),
    windows.confirm_delete_request_window(),

    windows.paths_info_window(),
    windows.select_num_stage(),
    windows.select_majors_window(),
    windows.confirm_path_window(),
    windows.complete_path_window(),

    windows.export_requests_window(),
)


@router.message(Command('request'), F.chat.type == ChatType.PRIVATE)
async def make_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    await dialog_manager.start(Request.select_category, mode=StartMode.RESET_STACK)


@router.callback_query(F.data.startswith('req_reject_'))
async def handle_reject_request(call: CallbackQuery, state: FSMContext):
    """Обработка нажатия кнопки отклонения с запросом причины"""
    _, _, req_id, current_stage = call.data.split('_')
    # Сохраняем данные в FSM
    await state.update_data(
        req_id=req_id,
        current_stage=current_stage,
        message_to_delete=call.message.message_id
    )
    # Запрашиваем причину отказа
    await call.message.edit_text(
        "Укажите причину отказа:",
        reply_markup=None
    )
    # Устанавливаем состояние ожидания причины
    await state.set_state("waiting_reject_reason")


@router.message(F.text, StateFilter("waiting_reject_reason"))
async def process_reject_reason(message: Message, state: FSMContext, bot):
    tz = timezone(const.TIME_ZONE)
    data = await state.get_data()
    req_id = ObjectId(data['req_id'])
    current_stage = int(data['current_stage'])
    user_id = message.from_user.id
    req = reqs.find_one({'_id': req_id})
    path = paths.find_one({'_id': req['path_id']})
    gpa_instance = gpa.find_one({'_id': req['gpa_id']})
    # Удаляем предыдущие сообщения
    try:
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=data['message_to_delete']
        )
        await message.delete()
    except Exception as e:
        await report_error(e)
    if not req:
        await message.answer("Запрос не найден!")
        return
    update_data = {
        f'stages.{current_stage}.status': 'reject',
        f'stages.{current_stage}.datetime': dt.datetime.now(),
        f'stages.{current_stage}.major_id': user_id,
        f'stages.{current_stage}.reason': message.text,
        'status': 'rejected',
        'reject_reason': message.text
    }
    reqs.update_one({'_id': req_id}, {'$set': update_data})
    try:
        await send_notify(req_id, gpa_instance, path, is_fallback=True, is_group=False, reason=message.text, is_rejected=True)
    except Exception as e:
        await report_error(e)
    author_name = (await bot.get_chat(req['author_id'])).full_name
    gpa_info = (
        f'<b>Ст.№ ГПА:</b> {gpa_instance["num_gpa"]}\n'
        f'<b>Наименование ГПА:</b> {gpa_instance["name_gpa"]}\n'
        f'<b>Тип ГПА:</b> {gpa_instance["type_gpa"]}\n'
        f'<b>Тип нагнетателя:</b> {gpa_instance["cbn_type"]}'
    )
    msg = (
        f'Вы <u>отклонили</u> запрос <b>#{req["req_num"]}</b>.\n\n'
        f"📅 Дата запроса: {req['datetime'].astimezone(tz).strftime('%d.%m.%Y %H:%M')}\n"
        f"🏭 Станция: {req['ks']}\n"
        f"👤 Автор: {author_name}\n\n"
        f"<u>Информация о ГПА:</u>\n{gpa_info}\n\n"
        f"<b>Текст запроса:</b>\n<blockquote>{req['text']}</blockquote>\n"
        f"<b>Причина отклонения:</b>\n<blockquote>{message.text}</blockquote>"
    )
    await message.answer(msg)
    await state.clear()


@router.callback_query(F.data.startswith('req_apply_'))
async def handle_apply_request(call: CallbackQuery):
    """Обработка нажатия кнопки согласования"""
    _, _, req_id, current_stage = call.data.split('_')
    current_stage = int(current_stage)
    req_id = ObjectId(req_id)
    user_id = call.from_user.id
    req = reqs.find_one({'_id': req_id})
    if not req:
        await call.answer("Запрос не найден!")
        return
    path = paths.find_one({'_id': req['path_id']})
    gpa_instance = gpa.find_one({'_id': req['gpa_id']})
    update_data = {
        f'stages.{current_stage}.status': 'apply',
        f'stages.{current_stage}.datetime': dt.datetime.now(),
        f'stages.{current_stage}.major_id': user_id
    }
    next_stage = current_stage + 1
    if next_stage > path['num_stages']:
        reqs.update_one({'_id': req_id}, {'$set': {**update_data, 'status': 'approved'}})
        try:
            # await send_notify(req_id, gpa_instance, path, is_fallback=False, is_group=True)  # Успешное согласование в группу
            await send_notify(req_id, gpa_instance, path, is_fallback=False, is_group=False)  # Успешное согласование автору
        except Exception as e:
            await report_error(e)
        await call.answer('Запрос полностью согласован!')
        await send_morning_report(update=True)
    else:
        reqs.update_one({'_id': req_id}, {'$set': {**update_data, 'current_stage': next_stage}})
        try:
            await send_request_to_major(req_id, next_stage)
            await call.answer('Запрос передан следующему согласующему')
        except Exception as e:
            await report_error(e)
    await call.message.delete()


@router.callback_query(F.data.startswith('launch_fail_'))
async def handle_fail_launch(call: CallbackQuery, state: FSMContext):
    _, _, req_id = call.data.split('_')
    # await call.message.delete()
    await state.update_data(req_id=req_id, message_to_delete=call.message.message_id)
    await call.message.edit_text(
        '❓ Укажите <u>причину</u>, почему пуск не был завершён:',
        reply_markup=None
    )
    await state.set_state('waiting_fail_reason')


@router.message(F.text, StateFilter("waiting_fail_reason"))
async def process_reject_reason(message: Message, state: FSMContext, bot):
    data = await state.get_data()
    req_id = ObjectId(data['req_id'])
    reason = message.text
    reqs.update_one(
        {'_id': req_id},
        {'$set': {'is_complete': True, 'fail_reason': reason, 'is_fail': True}}
    )
    req = reqs.find_one({'_id': req_id})
    req_date = req['request_datetime'].strftime('%d.%m.%Y %H:%M')
    gpa_instance = gpa.find_one({'_id': req['gpa_id']})
    # Удаляем предыдущие сообщения
    try:
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=data['message_to_delete']
        )
        await message.delete()
    except Exception as e:
        await report_error(e)
    msg_text = (f'🟠 Пуск <b>ГПА №{gpa_instance["num_gpa"]}</b> ({req["ks"]}), '
                f'который планировался на <u>{req_date}</u>, <b>не завершён</b> по причине:\n<blockquote>{reason}</blockquote>')
    stages_list = list(req['stages'].values())
    for i, stage in enumerate(stages_list):
        if i == len(stages_list) - 1:
            kb = InlineKeyboardBuilder()
            kb.button(text='🚫 Не создавать', callback_data=f"group_reject_{data['req_id']}")
            kb.button(text='👥 Создать группу', callback_data=f"group_apply_{data['req_id']}")
            msg_text = f'{msg_text}\n\nПри необходимости можете создать группу для расследования незавершенного пуска'
            await bot.send_message(
                chat_id=stage['major_id'],
                text=msg_text,
                reply_markup=kb.as_markup()
            )
        try:
            await bot.send_message(chat_id=stage['major_id'], text=msg_text,)
        except Exception as e:
            await report_error(e)
    await message.answer("Отправлено. Специалисты ПОЭКС уведомлены о причине.")
    await send_evening_report(update=True)
    await state.clear()


@router.callback_query(F.data.startswith('launch_success_'))
async def handle_success_launch(call: CallbackQuery):
    _, _, req_id = call.data.split('_')
    req_id = ObjectId(req_id)
    result = reqs.update_one(
        {'_id': req_id, 'is_complete': {'$ne': True}},
        {'$set': {'is_complete': True}}
    )
    try:
        await call.message.delete()
    except Exception as e:
        await report_error(e)
    if result.modified_count == 0:
        return
    req = reqs.find_one({'_id': req_id})
    req_date = req['request_datetime'].strftime('%d.%m.%Y %H:%M')
    gpa_instance = gpa.find_one({'_id': req['gpa_id']})
    for stage in req['stages'].values():
        try:
            await bot.send_message(
                chat_id=stage['major_id'],
                text=(
                    f'🟢 Пользователь подтвердил, что пуск <b>ГПА №{gpa_instance["num_gpa"]}</b> '
                    f'({req["ks"]}), который планировался на <u>{req_date}</u> завершён успешно'
                ),
                message_effect_id='5046509860389126442'
            )
        except Exception as e:
            await report_error(e)
    await send_evening_report(update=True)


@router.callback_query(F.data.startswith('req_files_'))
async def send_request_files(call: CallbackQuery):
    _, _, doc_type, req_id = call.data.split('_', 3)
    await show_req_files(call, doc_type, req_id)


@router.callback_query(F.data.startswith('hide_files_'))
async def hide_files(call: CallbackQuery):
    _, _, msg_ids = call.data.split('_')
    try:
        data = buffer.find_one({'_id': ObjectId(msg_ids)})
        for msg_id in data.get('sent_messages', []):
            try:
                await call.bot.delete_message(chat_id=call.message.chat.id, message_id=msg_id)
            except Exception as e:
                await report_error(e)
        try:
            await call.message.delete()
        except Exception as e:
            await report_error(e)
        buffer.delete_one({'_id': ObjectId(msg_ids)})
    except Exception as e:
        await report_error(e)


@router.callback_query(F.data.startswith('group_'))
async def make_group_decision(call: CallbackQuery):
    _, decision, req_id = call.data.split('_')
    if decision == 'reject':
        await call.message.delete()
    else:
        await create_group(req_id)


async def create_group(req_id):
    try:
        await app.start()
    except Exception as e:
        await report_error(e)
    req_id = ObjectId(req_id)
    req = reqs.find_one({'_id': req_id})
    date = req['request_datetime'].strftime('%d.%m.%Y')
    gpa_instance = gpa.find_one({'_id': req['gpa_id']})
    ks = req['ks']
    gpa_num = gpa_instance['num_gpa']
    ao_id = emergency_stops.insert_one({
        'date': date,
        'station': ks,
        'gpa': gpa_num,
        'gpa_id': gpa_instance['_id'],
        'is_unfinished_start': True
    }).inserted_id
    gpa_name = gpa_instance.get('name_gpa')
    ao_count = emergency_stops.count_documents(
        {'gpa_id': gpa_instance['_id'], '_id': { '$ne': ao_id }}
    )
    group_name = f'{ks} ГПА{gpa_num} {gpa_name} ({date})'
    try:
        group = await app.create_supergroup(group_name)
    except Exception as e:
        await report_error(e)
        return
    group_id = group.id
    groups.insert_one(
        {
            '_id': group_id,
            'group_name': group_name,
            'sub_banned': 'false',
            'ao_id': ao_id,
            'gpa_id': gpa_instance['_id']
        }
    )
    await app.set_chat_protected_content(chat_id=group_id, enabled=True)
    await app.set_chat_permissions(
        chat_id=group_id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_send_polls=True,
            can_add_web_page_previews=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True
        )
    )
    try:
        link = await app.create_chat_invite_link(group_id)
    except Exception as e:
        await report_error(e)
    try:
        await add_admin_to_group(BOT_ID, group_id)
    except Exception as e:
        await report_error(e)
    admin_users = list(admins.find({
        "$and": [
            {"$or": [{"sub": True}, {"sub": {"$exists": False}}]},
            {"user_id": {"$ne": int(MY_TELEGRAM_ID)}}
        ]
    }))
    invite_text = f'Группа для расследования незавершенного пуска: {link.invite_link}'
    for admin in admin_users:
        admin_id = admin.get('user_id')
        try:
            await add_admin_to_group(admin_id, group_id)
            # Задержка между добавлениями
            await asyncio.sleep(1)
        except:
            try:
                await bot.send_message(chat_id=admin_id, text=invite_text)
            except Exception as e:
                await report_error(e)
    try:
        await app.leave_chat(group_id)
    except Exception as e:
        await report_error(e)
    try:
        await bot.send_message(chat_id=OTKAZ_GROUP_ID, text=invite_text)
    except Exception as e:
        await report_error(e)
    post = await bot.send_message(chat_id=group_id, text=const.MANUAL)
    try:
        await bot.pin_chat_message(group_id, post.message_id)
        await bot.send_message(group_id, const.NEW_GROUP_TEXT)
    except Exception as e:
        await report_error(e)
    if ao_count > 0:
        await send_chat_links(gpa_instance, group_id, ao_id)
    await bot.send_message(MY_TELEGRAM_ID, text=f'Создана группа {group_name}')
