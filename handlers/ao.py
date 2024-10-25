import re
import datetime as dt

from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram import F, Router
from bson import ObjectId
from config.bot_config import bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode

from dialogs.for_ao import windows
from dialogs.for_ao.states import Ao
from dialogs.for_ao.selected import create_group
from config.telegram_config import MY_TELEGRAM_ID
from config.mongo_config import gpa, emergency_stops

SERVICE_MSG = ('Кто-то ввёл данные в группу "Отказы", '
               'но бот не смог ему отправить сообщение')
BAD_BOT_MSG = 'Бот не смог определить ГПА по сообщению в группе "Отказы"'
GPA_DETECT_TEXT = ('Автоматическое определение ГПА для создания '
                   'группы расследования отказа:')


router = Router()

dialog =  Dialog(
    windows.stations_window(),
    windows.shops_window(),
    windows.gpa_window(),
    windows.ao_confirm_window(),
    windows.finish_window(),
)


@router.message(Command('ao'))
async def ao_request(message: Message, dialog_manager: DialogManager):
    await message.delete()
    # Important: always set `mode=StartMode.RESET_STACK` you don't want to stack dialogs
    await dialog_manager.start(Ao.select_station, mode=StartMode.RESET_STACK)


@router.message(F.chat.id == -1001947065859)  # для pusha
# @router.message(F.chat.id == -1001902490328)
async def auto_otkaz_detect(message: Message):
    gpa_num_find = re.compile(r'№(\d\d|\d\d\d)')
    date_find = re.compile(r'\d\d\.\d\d\.(\d\d\d\d|\d\d)')
    lpu_find = re.compile(r'\w+ое\sЛПУМГ|\w+-\w+ое\sЛПУМГ')
    ks_find = re.compile(r'\w+ая|\w+ая')
    date = date_find.search(message.text)
    num_gpa = gpa_num_find.search(message.text)
    lpu = lpu_find.search(message.text)
    ks = ks_find.search(message.text)
    try:
        lpu_name = lpu.group()
    except AttributeError:
        lpu_name = None
    try:
        ks = f'{ks.group()} КС'
    except AttributeError:
        ks = None
    try:
        day, month, year = date.group().split('.')
        year = f'20{year}' if len(year) == 2 else year
        date = f'{day}.{month}.{year}'
    except AttributeError:
        date = dt.datetime.now().strftime('%d.%m.%Y')
    try:
        num_gpa = num_gpa.group()
    except AttributeError:
        num_gpa = None
    if lpu_name is not None and num_gpa is not None:
        queryset = list(gpa.find({'lpu': lpu_name, 'num_gpa': num_gpa[1:]}))
        if len(queryset) > 1 and ks is not None:
            gpa_instance = gpa.find_one({'lpu': lpu_name, 'num_gpa': num_gpa[1:], 'ks': ks})
            if gpa_instance is not None:
                await send_autodetect_message(message, gpa_instance)
        elif len(queryset) == 1:
            gpa_instance = queryset[0]
            await send_autodetect_message(message, gpa_instance)
        else:
            await bot.send_message(MY_TELEGRAM_ID, f'{BAD_BOT_MSG}\n\n{message.text}')
    elif ks is not None and num_gpa is not None:
        gpa_instance = gpa.find_one({'ks': ks, 'num_gpa': num_gpa[1:]})
        if gpa_instance is not None:
            await send_autodetect_message(message, gpa_instance)
        else:
            await bot.send_message(MY_TELEGRAM_ID, f'{BAD_BOT_MSG}\n\n{message.text}')
    else:
        await bot.send_message(MY_TELEGRAM_ID, f'{BAD_BOT_MSG}\n\n{message.text}')


async def send_autodetect_message(message, agr):
    station = agr['ks']
    gpa_num = agr['num_gpa']
    name_gpa = agr['name_gpa']
    ao_count = emergency_stops.count_documents({'gpa_id': agr['_id']})
    kb = InlineKeyboardBuilder()
    kb.button(
        text='Ввести данные вручную',
        callback_data='create_manual_none'
    )
    kb.button(
        text=f'Создать группу для ГПА №{gpa_num}',
        callback_data=f'create_auto_{str(agr["_id"])}'
    )
    kb.adjust(1)
    try:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=(f'{GPA_DETECT_TEXT}\n\n<b>{station}</b>\n<b>ГПА №{gpa_num}</b>\n\n'
                f'Согласно БД это: {name_gpa}\nКоличество зарегистрированных '
                f'АО (ВНО): {ao_count}\nСоздать группу для проведения '
                'расследования отказа этого ГПА?\nВы можете отказаться и ввести '
                'данные ГПА вручную.'),
            parse_mode='HTML',
            reply_markup=kb.as_markup()
        )
    except:
        await bot.send_message(MY_TELEGRAM_ID, SERVICE_MSG)


@router.callback_query(F.data.startswith('create'))
async def choose_mode(callback):
    _, choose, gpa_id = callback.data.split('_')
    if choose == 'auto':
        gpa_instance = gpa.find_one({'_id': ObjectId(gpa_id)})
        station = gpa_instance['ks']
        gpa_num = gpa_instance['num_gpa']
        date = dt.datetime.today().strftime('%d.%m.%Y')
        ao_id = emergency_stops.insert_one(
            {
                'date': date,
                'station': station,
                'gpa': gpa_num,
                'gpa_id': ObjectId(gpa_id)
            }
        ).inserted_id
        try:
            await create_group(None, ao_id, 'auto')
        except:
            await callback.message.answer('Создать группу автоматически не удалось, нажмите /ao')
            emergency_stops.delete_one({'_id': ao_id})
        try:
            await callback.message.delete()
        except:
            pass
    elif choose == 'manual':
        await callback.message.delete()
        await callback.message.answer('Для создания группы расследования нажмите /ao')
