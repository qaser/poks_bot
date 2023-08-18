from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation
from bson.objectid import ObjectId
from pyrogram.types import ChatPrivileges

from config.bot_config import bot
from config.mongo_config import petitions, users
from config.pyrogram_config import app
from config.telegram_config import MY_TELEGRAM_ID


async def create_group(call: types.CallbackQuery):
    _, pet_id = call.data.split('_')
    pet = petitions.find_one({'_id': ObjectId(pet_id)})
    user = pet.get('user_id')
    ks = pet.get('ks')
    log = pet.get('text')
    username = users.find_one({'user_id': user}).get('username')
    async with app:
        user_id = call.message.chat.id
        group_name = f'{ks} - {username}'
        try:
            group = await app.create_supergroup(group_name)
            await bot.send_message(MY_TELEGRAM_ID, text=f'Создана группа {group_name}')
        except:
            await call.message.answer(
                'Возникли проблемы при создании группы, повторите попытку позже'
            )
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Проблема при создании {group_name}'
            )
        group_id = group.id
        try:
            await app.promote_chat_member(
                chat_id= group_id,
                user_id=user_id,
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
                    is_anonymous=False
                )
            )
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Администратор группы "{group_name}" назначен'
            )
        except:
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Проблема при назначении администратора группы "{group_name}"'
            )
        try:
            await app.add_chat_members(group_id, user)
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Автор вопроса добавлен в группу "{group_name}"'
            )
        except:
            await call.message.answer(
                'Возникли проблемы c добавлением автора вопроса в группу'
            )
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Возникли проблемы c добавлением автора вопроса в группу {group_name}'
            )
        link = await app.create_chat_invite_link(group_id)
        await call.message.answer(link.invite_link)
        invite_text = f'Ваш вопрос приглашают обсудить в отдельном чате: {link.invite_link}'
        try:
            await bot.send_message(user, text=invite_text)
        except (CantInitiateConversation, BotBlocked):
            await call.message.answer(
                'Автор вопроса не доступен, возможно он заблокировал бота'
            )
        await app.send_message(group_id, text=f'Тема разговора:\n\n"{log}"')
        try:
            await app.leave_chat(group_id)
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Я удачно покинул группу {group_name}'
            )
        except:
            await bot.send_message(
                MY_TELEGRAM_ID,
                text=f'Почему-то я не покинул группу {group_name}'
            )


def register_callbacks_group(dp: Dispatcher):
    dp.register_callback_query_handler(
        create_group,
        Text(startswith='group'),
        state='*'
    )
