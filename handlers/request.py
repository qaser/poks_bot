import datetime as dt

from bson import ObjectId
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from config.bot_config import bot
from config.mongo_config import reqs, paths, gpa
from config.telegram_config import MY_TELEGRAM_ID, EXPLOIT_GROUP_ID
from dialogs.for_request import windows
from dialogs.for_request.states import Request
from dialogs.for_request.selected import send_request_to_major
from aiogram.enums import ChatType

from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext


router = Router()

dialog =  Dialog(
    windows.select_category_window(),
    windows.stations_window(),
    windows.shops_window(),
    windows.gpa_window(),
    windows.date_window(),
    windows.time_window(),
    windows.input_info_window(),
    windows.request_confirm_window(),
    windows.finish_window(),
    windows.paths_info_window(),  # 4 кнопки с типами путей
    windows.select_num_stage(),
    windows.select_majors_window(),
    windows.confirm_path_window(),
    windows.complete_path_window(),
)


@router.message(Command('request'), F.chat.type == ChatType.PRIVATE)
async def make_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    # print(message)
    await dialog_manager.start(Request.select_category, mode=StartMode.RESET_STACK)


@router.callback_query(F.data.startswith('req_'))
async def handle_request_decision(call: CallbackQuery, state: FSMContext):
    _, status, req_id, current_stage = call.data.split('_')
    current_stage = int(current_stage)
    req_id = ObjectId(req_id)
    user_id = call.from_user.id
    # Получаем актуальные данные запроса
    req = reqs.find_one({'_id': req_id})
    gpa_instance = gpa.find_one({'_id': req['gpa_id']})
    if not req:
        await call.answer("Запрос не найден!")
        return
    path = paths.find_one({'_id': req['path_id']})
    num_stages = path['num_stages']
    # Обновляем запись в БД
    update_data = {
        f'stages.{current_stage}.status': status,
        f'stages.{current_stage}.datetime': dt.datetime.now(),
        f'stages.{current_stage}.major_id': user_id
    }
    if status == 'reject':
        # Обработка отклонения
        reqs.update_one(
            {'_id': req_id},
            {'$set': {
                **update_data,
                'status': 'rejected'
            }}
        )
        # Уведомляем автора
        try:
            await bot.send_message(
                req['author_id'],
                f"🔴 Ваш запрос отклонён на этапе {current_stage}\n"
                f"Причина: {call.message.text.split('Причина:')[1] if 'Причина:' in call.message.text else 'не указана'}"
            )
        except Exception as e:
            print(f"Ошибка уведомления автора: {e}")
        await call.answer("Запрос отклонён. Автор заявки будет уведомлён об этом")
        await call.message.edit_reply_markup()  # Убираем кнопки
    elif status == 'apply':
        # Обработка согласования
        next_stage = current_stage + 1
        if next_stage > path['num_stages']:
            # Все этапы пройдены
            reqs.update_one(
                {'_id': req_id},
                {'$set': {
                    **update_data,
                    'status': 'approved'
                }}
            )
            # Уведомляем автора
            try:
                await bot.send_message(
                    req['author_id'],
                    f"🟢 Ваш запрос полностью согласован!\n"
                    f"Все этапы пройдены успешно"
                )
            except Exception as e:
                print(f"Ошибка уведомления автора: {e}")
            # try:
                # gpa_info = (
                #     f'<b>Ст.№ ГПА:</b> {gpa_instance["num_gpa"]}\n'
                #     f'<b>Наименование ГПА:</b> {gpa_instance["name_gpa"]}\n'
                # )
                # stages_text = ''
                # for stage_num in range(1, num_stages + 1):
                #     stage_data = req['stages'].get(str(stage_num), {})
                #     status = stage_data.get('status', 'inwork' if stage_num == current_stage else 'pending')
                #     icon = ('🟢' if status == 'apply' else
                #         '🔴' if status == 'reject' else
                #         '⚫' if status == 'pass' else '⚪')
                #     major_name = 'ожидается'
                #     if 'major_id' in stage_data:
                #         try:
                #             major_chat = await bot.get_chat(stage_data['major_id'])
                #             major_name = major_chat.full_name
                #         except:
                #             major_name = "недоступен"
                #     date_str = stage_data.get('datetime', '').strftime('%d.%m.%Y %H:%M') if 'datetime' in stage_data else ""
                #     stages_text += f"{icon} Этап {stage_num} - {major_name}" + (f" ({date_str})" if date_str else "") + "\n"
                # request_text = (
                #     f"<b>Информация о согласовании пуска ГПА</b>\n\n"
                #     f"📅 Дата запроса: {req['datetime'].strftime('%d.%m.%Y %H:%M')}\n"
                #     f"🏭 Станция: {req['ks']}\n\n"
                #     f'<u>Информация о ГПА:</u>\n{gpa_info}\n\n'
                #     # f"<b>Статус согласования:</b>\n{stages_text}\n"
                #     f"<b>Текст запроса:</b>\n<i>{req['text']}</i>\n\n"
                # )
                # await bot.send_message(
                #     chat_id=EXPLOIT_GROUP_ID,
                #     text='123',
                #     # message_thread_id=SPCH_THREAD_ID
                # )
            # except Exception as e:
            #     print(f"Ошибка уведомления группы: {e}")
            # await call.answer("Запрос полностью согласован!")
            # await call.message.edit_reply_markup()  # Убираем кнопки
        else:
            # Переходим к следующему этапу
            reqs.update_one(
                {'_id': req_id},
                {'$set': {
                    **update_data,
                    'current_stage': next_stage
                }}
            )
            # Отправляем запрос следующему согласующему
            try:
                await send_request_to_major(req_id, next_stage)
                await call.answer("Запрос передан следующему согласующему")
                await call.message.edit_reply_markup()  # Убираем кнопки
            except Exception as e:
                print(f"Ошибка отправки следующему согласующему: {e}")
                await call.answer("Ошибка при передаче запроса", show_alert=True)
