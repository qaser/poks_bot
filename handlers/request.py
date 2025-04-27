import datetime as dt

from bson import ObjectId
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from config.bot_config import bot
from config.mongo_config import reqs, paths
from config.telegram_config import MY_TELEGRAM_ID, OTKAZ_GROUP_ID
from dialogs.for_request import windows
from dialogs.for_request.states import Request
from dialogs.for_request.selected import send_request_to_major
from aiogram.enums import ChatType

from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext


router = Router()

dialog =  Dialog(
    windows.stations_window(),
    windows.shops_window(),
    windows.gpa_window(),
    windows.input_info_window(),
    windows.request_confirm_window(),
    windows.finish_window(),
)


@router.message(Command('request'), F.chat.type == ChatType.PRIVATE)
async def make_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    # print(message)
    await dialog_manager.start(Request.select_station, mode=StartMode.RESET_STACK)


@router.callback_query(F.data.startswith('req_'))
async def handle_request_decision(call: CallbackQuery, state: FSMContext):
    _, status, req_id, current_stage = call.data.split('_')
    current_stage = int(current_stage)
    req_id = ObjectId(req_id)
    user_id = call.from_user.id
    # Получаем актуальные данные запроса
    req = reqs.find_one({'_id': req_id})
    if not req:
        await call.answer("Запрос не найден!")
        return
    path = paths.find_one({'_id': req['path_id']})
    if not path:
        await call.answer("Путь согласования не найден!")
        return
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
        await call.answer("Запрос отклонён")
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
            await call.answer("Запрос полностью согласован!")
            await call.message.edit_reply_markup()  # Убираем кнопки
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
