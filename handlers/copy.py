from time import sleep

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config.bot_config import bot
from config.pyrogram_config import app
from config.telegram_config import MY_TELEGRAM_ID

router = Router()


@router.message(Command('copy'))
async def hash_users(message: Message):
    group_id = message.chat.id
    try:
        await message.delete()
    except:
        pass
    try:
        await app.start()
    except:
        pass
    try:
        link = await app.create_chat_invite_link(group_id)
        await app.join_chat(link.invite_link)
        await bot.send_message(MY_TELEGRAM_ID, text='Создана ссылка и я вошел в группу')
    except:
        pass
    try:
        await app.set_chat_protected_content(
            chat_id=message.chat.id,
            enabled=False
        )
        msg = await message.answer('30', disable_notification=True)
        for sec in range(29, 0, -2):
            await msg.edit_text(str(sec))
            sleep(2)
    except:
        await bot.send_message(MY_TELEGRAM_ID, text='Не получилось снять с группы защиту')
    try:
        await app.set_chat_protected_content(
            chat_id=message.chat.id,
            enabled=True
        )
    except:
        await bot.send_message(MY_TELEGRAM_ID, text='Не получилось установить на группу защиту')
    try:
        await msg.delete()
    except:
        pass
    try:
        await app.leave_chat(message.chat.id)
        await bot.send_message(MY_TELEGRAM_ID, text='Я покинул группу')
    except Exception:
        pass
    try:
        await bot.send_message(MY_TELEGRAM_ID, 'нажата кнопка /copy')
    except:
        pass
    try:
        await message.delete()
    except:
        pass
