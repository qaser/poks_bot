import datetime as dt
import asyncio

from aiogram import F, Router
from aiogram.types import Message

from config.bot_config import bot
from aiogram.filters import Command
from config.mongo_config import users_collection, messages_collection, migration_status_collection
from config.telegram_config import MY_TELEGRAM_ID, NEW_OTKAZ_GROUP, OTKAZ_GROUP_ID
from config.pyrogram_config import app
from utils.utils import report_error

router = Router()


async def save_chat_members(chat_id: int):
    """Сохраняет всех участников группы"""
    try:
        members_count = 0
        # Получаем администраторов (это доступно боту)
        administrators = await bot.get_chat_administrators(chat_id)

        for admin in administrators:
            user = admin.user
            if await save_user(user):
                members_count += 1

        print(f"Сохранено участников: {members_count}")
        return members_count

    except Exception as e:
        print(f"Ошибка при сохранении участников: {e}")
        return 0


async def save_user(user) -> bool:
    """Сохраняет пользователя в базу данных"""
    try:
        user_data = {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_bot": user.is_bot,
            "saved_at": dt.datetime.now()
        }

        users_collection.update_one(
            {"user_id": user.id},
            {"$set": user_data},
            upsert=True
        )
        return True

    except Exception as e:
        print(f"Ошибка при сохранении пользователя: {e}")
        return False


async def migrate_messages_to_new_chat():
    """Переносит сообщения в новую группу"""
    try:
        # Получаем все сохраненные сообщения
        messages = list(messages_collection.find().sort("date", 1))

        print(f"Начинаем перенос {len(messages)} сообщений")

        failed_messages = []
        success_count = 0

        for message_data in messages:
            try:
                # Пауза между сообщениями чтобы не превысить лимиты
                await asyncio.sleep(0.5)

                # Отправляем сообщение
                await bot.send_message(
                    chat_id=NEW_OTKAZ_GROUP,
                    text=f"💬 {message_data['text']}\n\n"
                         f"📅 Оригинальное сообщение от {message_data['date'].strftime('%Y-%m-%d %H:%M')}"
                )
                success_count += 1

                print(f"Отправлено сообщений: {success_count}/{len(messages)}")

            except Exception as e:
                print(f"Ошибка при отправке сообщения {message_data['message_id']}: {e}")
                failed_messages.append({
                    "message_id": message_data["message_id"],
                    "error": str(e)
                })

        print(f"Успешно отправлено: {success_count}, ошибок: {len(failed_messages)}")
        return success_count, failed_messages

    except Exception as e:
        print(f"Ошибка при переносе сообщений: {e}")
        return 0, []


async def invite_users_to_new_chat():
    """Добавляет участников в новую группу"""
    try:
        users = list(users_collection.find({"is_bot": False}))  # Не приглашаем ботов
        failed_invites = []
        success_count = 0

        print(f"Пытаемся добавить {len(users)} пользователей")

        for user_data in users:
            try:
                user_id = user_data["user_id"]

                # Пытаемся добавить пользователя напрямую
                try:
                    await bot.ban_chat_member(NEW_OTKAZ_GROUP, user_id)
                    await asyncio.sleep(0.1)
                    await bot.unban_chat_member(NEW_OTKAZ_GROUP, user_id)

                    success_count += 1
                    print(f"Пользователь {user_id} добавлен")

                except Exception as invite_error:
                    # Если прямое добавление невозможно, создаем ссылку-приглашение
                    try:
                        invite_link = await bot.create_chat_invite_link(
                            NEW_OTKAZ_GROUP,
                            member_limit=1,
                            creates_join_request=True
                        )

                        # Здесь нужно отправить ссылку пользователю
                        # Но для этого бот должен быть в личной переписке с пользователем

                        failed_invites.append({
                            "user_id": user_id,
                            "username": user_data.get("username"),
                            "error": "Требуется ручное приглашение",
                            "invite_link": invite_link.invite_link
                        })

                    except Exception as link_error:
                        failed_invites.append({
                            "user_id": user_id,
                            "username": user_data.get("username"),
                            "error": str(link_error)
                        })

                # Пауза между запросами
                await asyncio.sleep(1)

            except Exception as e:
                print(f"Ошибка с пользователем {user_data['user_id']}: {e}")
                failed_invites.append({
                    "user_id": user_data["user_id"],
                    "username": user_data.get("username"),
                    "error": str(e)
                })

        print(f"Успешно добавлено: {success_count}, ошибок: {len(failed_invites)}")

        # Сохраняем список неудачных приглашений
        migration_status_collection.update_one(
            {"migration_type": "user_invites"},
            {"$set": {
                "failed_invites": failed_invites,
                "success_count": success_count,
                "processed_at": dt.datetime.now()
            }},
            upsert=True
        )

        return success_count, failed_invites

    except Exception as e:
        print(f"Ошибка при добавлении пользователей: {e}")
        return 0, []


async def save_chat_history(chat_id: int):
    """Сохраняет всю историю сообщений из группы"""
    try:
        # Получаем информацию о чате
        chat = await bot.get_chat(chat_id)
        print(f"Начинаем сохранение истории для чата: {chat.title}")

        # Сохраняем участников
        await save_chat_members(chat_id)

        # Получаем и сохраняем сообщения
        message_count = 0
        last_message_id = None

        while True:
            messages = await get_messages_batch(chat_id, last_message_id)
            if not messages:
                break

            for message in messages:
                if await save_message(message):
                    message_count += 1
                last_message_id = message.message_id

            print(f"Сохранено сообщений: {message_count}")

            # Пауза чтобы не превысить лимиты API
            await asyncio.sleep(0.1)

        print(f"Всего сохранено сообщений: {message_count}")
        return message_count

    except Exception as e:
        print(f"Ошибка при сохранении истории: {e}")
        return 0


async def save_message(message: Message) -> bool:
    """Сохраняет одно сообщение в базу данных"""
    try:
        # Пропускаем сообщения без текста
        if not message.text and not message.caption:
            return False

        message_data = {
            "message_id": message.message_id,
            "chat_id": message.chat.id,
            "user_id": message.from_user.id if message.from_user else None,
            "text": message.text or message.caption,
            "date": message.date,
            "content_type": message.content_type,
            "saved_at": dt.datetime.now()
        }

        messages_collection.insert_one(message_data)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении сообщения: {e}")
        return False


async def get_messages_batch(chat_id: int, last_message_id: int = None):
    """Получает пачку сообщений (до 100) используя Pyrogram"""
    try:
        messages = []
        limit = 100

        # Если указан last_message_id, получаем сообщения после него
        if last_message_id:
            messages = await app.get_chat_history(
                chat_id=chat_id,
                limit=limit,
                offset_id=last_message_id
            )
        else:
            # Первый запрос - получаем последние сообщения
            messages = await app.get_chat_history(
                chat_id=chat_id,
                limit=limit
            )

        # Преобразуем асинхронный генератор в список
        messages_list = []
        async for message in messages:
            messages_list.append(message)
            if len(messages_list) >= limit:
                break
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=f"Получено {len(messages_list)} сообщений из чата {chat_id}"
        )
        return messages_list

    except Exception as e:
        print(f"Ошибка при получении сообщений через Pyrogram: {e}")
        return []


async def get_all_chat_messages(chat_id: int):
    """Получает все сообщения из чата"""
    all_messages = []
    last_message_id = None
    total_messages = 0

    print("🚀 Начинаем получение истории сообщений...")

    while True:
        messages_batch = await get_messages_batch(chat_id, last_message_id)

        if not messages_batch:
            break

        # Добавляем сообщения в общий список
        for message in messages_batch:
            all_messages.append(message)
            last_message_id = message.id
            total_messages += 1

        print(f"📥 Получено сообщений: {total_messages}")

        # Если получено меньше limit, значит это последняя пачка
        if len(messages_batch) < 100:
            break

        # Пауза чтобы не превысить лимиты Telegram API
        await asyncio.sleep(1)

    print(f"✅ Всего получено сообщений: {total_messages}")
    return all_messages


async def save_pyrogram_message(message) -> bool:
    """Сохраняет сообщение из Pyrogram в MongoDB"""
    try:
        # Пропускаем сообщения без текста
        if not message.text and not message.caption:
            return False

        # Извлекаем информацию о пользователе
        user_id = None
        username = None
        first_name = None

        if message.from_user:
            user_id = message.from_user.id
            username = message.from_user.username
            first_name = message.from_user.first_name

        message_data = {
            "message_id": message.id,
            "chat_id": message.chat.id,
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "text": message.text or message.caption or "",
            "date": message.date,
            "message_type": str(message.service) if message.service else "text",
            "media_type": str(message.media) if message.media else None,
            "has_media": bool(message.media),
            "saved_at": dt.datetime.now()
        }

        # Сохраняем с обработкой дубликатов
        result = messages_collection.update_one(
            {
                "message_id": message.id,
                "chat_id": message.chat.id
            },
            {"$set": message_data},
            upsert=True
        )

        return True

    except Exception as e:
        print(f"Ошибка при сохранении сообщения {message.id}: {e}")
        return False


async def get_all_chat_members(chat_id: int):
    """Получает всех участников группы через Pyrogram"""
    try:
        members = []
        total_members = 0

        print("👥 Начинаем получение списка участников...")

        async for member in app.get_chat_members(chat_id):
            members.append(member)
            total_members += 1
            print(f"Получено участников: {total_members}")

            # Пауза чтобы не превысить лимиты
            if total_members % 50 == 0:
                await asyncio.sleep(1)

        print(f"✅ Всего получено участников: {total_members}")
        return members

    except Exception as e:
        print(f"Ошибка при получении участников: {e}")
        return []


async def save_chat_members_pyrogram(chat_id: int):
    """Сохраняет всех участников группы через Pyrogram"""
    try:
        members = await get_all_chat_members(chat_id)
        saved_count = 0

        for member in members:
            user = member.user
            if await save_user_from_pyrogram(user):
                saved_count += 1

        print(f"💾 Сохранено участников в базу: {saved_count}")
        return saved_count

    except Exception as e:
        print(f"Ошибка при сохранении участников: {e}")
        return 0


async def save_user_from_pyrogram(user) -> bool:
    """Сохраняет пользователя из Pyrogram в MongoDB"""
    try:
        user_data = {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_bot": user.is_bot,
            "is_premium": getattr(user, 'is_premium', False),
            "language_code": user.language_code,
            "saved_at": dt.datetime.now()
        }

        users_collection.update_one(
            {"user_id": user.id},
            {"$set": user_data},
            upsert=True
        )
        return True

    except Exception as e:
        print(f"Ошибка при сохранении пользователя {user.id}: {e}")
        return False


@router.message(Command('migrate'))
async def complete_migration(message: Message):
    """Выполняет полную миграцию"""
    await bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text="🚀 Начало миграции..."
    )
    try:
        # 1. Сохраняем историю сообщений через Pyrogram
        all_messages = await get_all_chat_messages(OTKAZ_GROUP_ID)

        # Сохраняем каждое сообщение
        saved_count = 0
        for message in all_messages:
            if await save_pyrogram_message(message):
                saved_count += 1

        # 2. Сохраняем участников через Pyrogram
        saved_users = await save_chat_members_pyrogram(OTKAZ_GROUP_ID)

        # 3. Переносим сообщения в новую группу (используем aiogram)
        # print("📤 Переносим сообщения в новую группу...")
        # migrated_messages, failed_messages = await migrate_messages_to_new_chat()

        # # 4. Добавляем участников
        # print("➕ Добавляем участников в новую группу...")
        # invited_users, failed_invites = await invite_users_to_new_chat()

        # 5. Формируем отчет
        report = f"""
            📊 ОТЧЕТ О МИГРАЦИИ (Pyrogram)

            ✅ Успешно:
            - Получено сообщений через Pyrogram: {len(all_messages)}
            - Сохранено сообщений в базу: {saved_count}
            - Сохранено пользователей: {saved_users}
        """

        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=report
        )

    except Exception as e:
        await report_error(e)
