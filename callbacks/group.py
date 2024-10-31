from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation
from bson.objectid import ObjectId
from pyrogram.types import ChatPrivileges

from config.bot_config import bot
from config.mongo_config import admins, petitions, users
from config.pyrogram_config import app
from config.telegram_config import BOT_ID, MY_TELEGRAM_ID


async def create_group(call: types.CallbackQuery):
    _, pet_id = call.data.split('_')
    pet = petitions.find_one({'_id': ObjectId(pet_id)})
    group_link = pet.get('group_link')  # (group_creator, group_link)
    if group_link is not None:
        group_creator, g_link = group_link
        g_username = admins.find_one({'user_id': group_creator}).get('username')
        await call.message.answer(
            f'Рабочая группа уже создана специалистом ПОЭКС: {g_username}\n{g_link}'
        )
    else:
        user = pet.get('user_id')
        ks = pet.get('ks')
        log = pet.get('text')
        username = users.find_one({'user_id': user}).get('username')
        msg = await call.message.answer('Начинается процесс создания рабочего чата...')
        async with app:
            user_id = call.message.chat.id
            group_name = f'{ks} - {username}'
            try:
                group = await app.create_supergroup(group_name)
                group_id = group.id
                await app.set_chat_protected_content(chat_id=group_id, enabled=True)
                await bot.send_message(MY_TELEGRAM_ID, text=f'Создана группа {group_name}')
                await msg.edit_text('Группа создана.\n Идет процесс назначения администратора...')
            except:
                await msg.edit_text(
                    'Возникли проблемы при создании группы, повторите попытку позже'
                )
                await bot.send_message(
                    MY_TELEGRAM_ID,
                    text=f'Проблема при создании {group_name}'
                )
            link = await app.create_chat_invite_link(group_id)
            invite_text = f'Ваш вопрос приглашают обсудить в отдельном чате: {link.invite_link}'
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
                await msg.edit_text('Вы назначены администратором.\nДобавляю собеседника...')
            except:
                await bot.send_message(
                    MY_TELEGRAM_ID,
                    text=f'Проблема при назначении администратора группы "{group_name}"'
                )
                await msg.edit_text('Проблема с процессом назначения администратора :(\n Перейдите по ссылке')
                await call.message.answer(link.invite_link)
            try:
                await app.add_chat_members(group_id, user)
                try:
                    await bot.send_message(user, text=invite_text)
                except (CantInitiateConversation, BotBlocked):
                    pass
                await bot.send_message(
                    MY_TELEGRAM_ID,
                    text=f'Автор вопроса добавлен в группу "{group_name}"'
                )
                await msg.edit_text('Собеседник добавлен')
            except:
                try:
                    await bot.send_message(user, text=invite_text)
                    await msg.edit_text(
                        'Бот не смог добавить автора вопроса, но он получил ссылку на доступ в группу'
                    )
                    await bot.send_message(
                        MY_TELEGRAM_ID,
                        text=f'Автор вопроса получил ссылку на доступ в группу {group_name}'
                    )
                except (CantInitiateConversation, BotBlocked):
                    await call.message.answer(
                        'Автор вопроса не доступен, возможно он заблокировал бота'
                    )
            petitions.update_one(
                {'_id': ObjectId(pet_id)},
                {'$set': {'group_link': (user_id, link.invite_link)}}
            )
            await msg.edit_text(link.invite_link)
            await app.promote_chat_member(
                chat_id=group_id,
                user_id=BOT_ID,
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
            await bot.send_message(group_id, text=f'Тема разговора:\n\n"{log}"')
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
