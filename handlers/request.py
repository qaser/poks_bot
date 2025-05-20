import datetime as dt

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode
from bson import ObjectId

from config.bot_config import bot
from config.mongo_config import buffer, gpa, paths, reqs
# from config.telegram_config import EXPLOIT_GROUP_ID, MY_TELEGRAM_ID
from dialogs.for_request import windows
from dialogs.for_request.selected import (send_notify, send_request_to_major,
                                          show_req_files)
from dialogs.for_request.states import Request

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
    windows.select_resource_act_window(),
    windows.input_resource_act_file_window(),  # каждый 2-ой запрос
    windows.input_out_of_resource_reason_window(),

    windows.select_protocol_window(),
    windows.input_protocol_file_window(),  # каждый 4-ой запрос

    windows.select_card_window(),
    windows.input_card_file_window(),  # каждый 6-ой запрос

    windows.show_reject_window(),
    windows.input_info_window(),
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
        print(f"Ошибка при удалении сообщений: {e}")
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
        pass
    await message.answer("Запрос отклонён. Автор заявки уведомлён о причине.")
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
            print(f'Ошибка уведомления группы: {e}')
        await call.answer('Запрос полностью согласован!')
    else:
        reqs.update_one({'_id': req_id}, {'$set': {**update_data, 'current_stage': next_stage}})
        try:
            await send_request_to_major(req_id, next_stage)
            await call.answer('Запрос передан следующему согласующему')
        except Exception as e:
            print(f'Ошибка отправки следующему согласующему: {e}')
            await call.answer('Ошибка при передаче запроса', show_alert=True)
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
        print(f"Ошибка при удалении сообщений: {e}")
    stages = req['stages']
    for stage in stages.values():
        try:
            await bot.send_message(
                chat_id=stage['major_id'],
                text=(
                    f'🟠 Пуск <b>ГПА №{gpa_instance["num_gpa"]}</b> ({req["ks"]}), '
                    f'который планировался на <u>{req_date}</u>, <b>не завершён</b> по причине:\n<i>{reason}</i>'
                ),
            )
        except:
            pass
    await message.answer("Отправлено. Специалисты ПОЭКС уведомлены о причине.")
    await state.clear()


@router.callback_query(F.data.startswith('launch_success_'))
async def handle_success_launch(call: CallbackQuery):
    _, _, req_id = call.data.split('_')
    await call.message.delete()
    req_id = ObjectId(req_id)
    req = reqs.find_one({'_id': req_id})
    reqs.update_one({'_id': req_id}, {'$set': {'is_complete': True}})
    req_date = req['request_datetime'].strftime('%d.%m.%Y %H:%M')
    gpa_instance = gpa.find_one({'_id': req['gpa_id']})
    stages = req['stages']
    for stage in stages.values():
        try:
            await bot.send_message(
                chat_id=stage['major_id'],
                text=(
                    f'🟢 Пользователь подтвердил, что пуск <b>ГПА №{gpa_instance["num_gpa"]}</b> '
                    f'({req["ks"]}), который планировался на <u>{req_date}</u> завершён успешно'
                ),
                message_effect_id='5046509860389126442'
            )
        except:
            pass


@router.callback_query(F.data.startswith('req_files_'))
async def send_request_files(call: CallbackQuery):
    _, _, req_id = call.data.split('_')[:3]
    await show_req_files(call, req_id)


@router.callback_query(F.data.startswith('hide_files_'))
async def hide_files(call: CallbackQuery):
    _, _, msg_ids = call.data.split('_')
    try:
        data = buffer.find_one({'_id': ObjectId(msg_ids)})
        for msg_id in data.get('sent_messages', []):
            try:
                await call.bot.delete_message(chat_id=call.message.chat.id, message_id=msg_id)
            except Exception as e:
                pass
        try:
            await call.message.delete()
        except Exception as e:
            pass
        buffer.delete_one({'_id': ObjectId(msg_ids)})
    except Exception:
        await call.answer("Ошибка при скрытии файлов", show_alert=True)
