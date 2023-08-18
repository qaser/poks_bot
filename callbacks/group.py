from aiogram import Dispatcher,types
from config.bot_config import bot
from aiogram.dispatcher.filters import Text
from bson.objectid import ObjectId
from pyrogram.types import ChatPrivileges
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation

from config.mongo_config import petitions, users
from config.pyrogram_config import app


async def create_group(call: types.CallbackQuery):
    _, pet_id = call.data.split('_')
    pet = petitions.find_one({'_id': ObjectId(pet_id)})
    user = pet.get('user_id')
    ks = pet.get('ks')
    # log = pet.get('conversation')
    username = users.find_one({'user_id': user}).get('username')
    async with app:
        user_id = call.message.chat.id
        group_name = f'{ks} - {username}'
        group = await app.create_supergroup(group_name)
        group_id = group.id
        # await group.add_members(1835903546)
        # await app.add_chat_members(group_id, user_id)
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
        await app.add_chat_members(group_id, user)
        link = await app.create_chat_invite_link(group_id)
        await call.message.answer(link.invite_link)
        invite_text = f'Ваш вопрос приглашают обсудить в отдельном чате: {link.invite_link}'
        try:
            await bot.send_message(user, text=invite_text)
        except (CantInitiateConversation, BotBlocked):
            pass
        await app.leave_chat(group_id)


def register_callbacks_group(dp: Dispatcher):
    dp.register_callback_query_handler(
        create_group,
        Text(startswith='group'),
        state='*'
    )
