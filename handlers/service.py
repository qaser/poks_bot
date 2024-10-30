from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from config.bot_config import bot
from config.mongo_config import archive, groups, admins
from config.telegram_config import MY_TELEGRAM_ID
from utils import constants as const


router = Router()


# запрет на рассылку уведомлений
@router.message(Command('unsub'))
async def stop_subscribe(message: Message):
    group_id = message.chat.id
    group_check = groups.find_one({'_id': group_id})
    if group_check is not None:
        groups.update_one(
            {'_id': group_id},
            {'$set': {'sub_banned': 'true'}},
            upsert=False
        )
        await message.answer('Напоминания для этой группы отключены')
    await message.delete()


# включение рассылки уведомлений
@router.message(Command('sub'))
async def start_subscribe(message: Message):
    group_id = message.chat.id
    group_check = groups.find_one({'_id': group_id})
    if group_check is not None:
        groups.update_one(
            {'_id': group_id},
            {'$set': {'sub_banned': 'false'}},
            upsert=False
        )
        await message.answer('Напоминания для этой группы включены')
    await message.delete()


@router.message(Command('log'))
async def send_logs(message: Message):
    user_id = message.from_user.id
    if user_id == int(MY_TELEGRAM_ID):
        document = FSInputFile(path=r'logs_bot.log')
        await message.answer_document(document=document)
    await message.delete()


# обработка команды /admins
@router.message(Command('admins'))
async def check_admins(message: Message):
    await message.delete()
    queryset = list(admins.find({}))
    res_text = ''
    dir_list = []
    for adm in queryset:
        if adm.get('user_id') == int(MY_TELEGRAM_ID):
            continue
        name = adm.get('username')
        directions = adm.get('directions')
        dir_text = ''
        for dir in directions:
            if dir not in dir_list:
                dir_list.append(dir)
            dir_text = f'{dir_text}    {const.DIRECTIONS_CODES[dir]}\n'
        res_text = f'{res_text}\n<b>{name}:</b>\n{dir_text}'
        dirs_not_used = []
        for code, name in const.DIRECTIONS_CODES.items():
            if code not in dir_list:
                dirs_not_used.append(name)
        if len(dirs_not_used) == 0:
            summary = '<u>На все направления назначены специалисты</u>'
        else:
            res = ''
            for i in dirs_not_used:
                res = f'{res}{i}\n'
            summary = f'<u>Направления без отслеживания:</u>\n{res}'
    await message.answer(
        text=f'{res_text}\n{summary}',
        parse_mode='HTML'
    )


# обработка команды /links
@router.message(Command('links'))
async def check_groups(message: Message):
    queryset = list(groups.find({'sub_banned': 'false'}))
    for link in queryset:
        try:
            invite_link = await bot.create_chat_invite_link(chat_id=link['_id'])
            await bot.send_message(MY_TELEGRAM_ID, invite_link.invite_link)
        except Exception as e:
            pass
