from aiogram import F, Router
from aiogram.types import Message, FSInputFile
import pprint

from config.bot_config import bot
from config.mongo_config import archive
from config.telegram_config import MY_TELEGRAM_ID


router = Router()

@router.message(F.content_type.in_({'text', 'video', 'photo', 'document'}))
async def archive_messages(message: Message):
    chat = message.chat.id
    # pprint.pprint(message)
    if message.photo:
        await bot.send_photo(
            MY_TELEGRAM_ID,
            photo=message.photo[-1].file_id,
            caption=message.chat.full_name
        )
    if message.document:
        await bot.send_document(
            MY_TELEGRAM_ID,
            document=getattr(message, 'document').file_id,
            caption=message.chat.full_name
        )
    if message.video:
        await bot.send_video(
            MY_TELEGRAM_ID,
            video=getattr(message, 'video').file_id,
            caption=message.chat.full_name
        )
    if message.text:
        data = archive.find_one({'_id': chat})
        if data is None:
            archive.insert_one({'_id': chat, 'messages': [message.text]})
        else:
            data.get('messages').append(message.text)
            archive.update_one(
                {'_id': chat},
                {'$set': {'messages': data.get('messages')}},
                upsert=False
            )
        chat_name = message.chat.full_name
        await bot.send_message(MY_TELEGRAM_ID, f'{chat_name}: {message.text}')
