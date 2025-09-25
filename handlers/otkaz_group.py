import datetime as dt
import asyncio

from aiogram import F, Router
from aiogram.types import Message

from config.bot_config import bot
from aiogram.filters import Command
from config.mongo_config import users_collection, messages_collection, migration_status_collection
from config.telegram_config import MY_TELEGRAM_ID, NEW_OTKAZ_GROUP, OTKAZ_GROUP_ID

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


async def get_messages_batch(chat_id: int, last_message_id = None):
    """Получает пачку сообщений (до 100)"""
    try:
        # Используем get_chat для получения информации о чате
        chat = await bot.get_chat(chat_id)

        # Для получения истории сообщений нужно использовать forward_from_chat
        # или другие методы, но бот должен иметь доступ к сообщениям

        # Альтернативный подход: слушать новые сообщения и запрашивать историю
        # Это более сложно, так как бот не может просто получить всю историю

        # Вместо этого, можно использовать метод get_chat_administrators
        # и другие доступные методы для получения максимальной информации

        return []

    except Exception as e:
        print(f"Ошибка при получении сообщений: {e}")
        return []


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


@router.message(Command('migrate'))
async def complete_migration(message: Message):
    """Выполняет полную миграцию"""
    await bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text="🚀 Начало миграции..."
    )
    # 1. Сохраняем историю исходной группы
    await bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text="📥 Сохраняем историю сообщений..."
    )
    saved_messages = await save_chat_history(OTKAZ_GROUP_ID)

    # 2. Сохраняем участников
    await bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text="👥 Сохраняем участников..."
    )
    saved_users = await save_chat_members(OTKAZ_GROUP_ID)

    # # 3. Переносим сообщения
    # print("📤 Переносим сообщения...")
    # migrated_messages, failed_messages = await migrate_messages_to_new_chat()

    # # 4. Добавляем участников
    # print("➕ Добавляем участников...")
    # invited_users, failed_invites = await invite_users_to_new_chat()

    # 5. Формируем отчет
    await bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text="📊 Формируем отчет..."
    )

    report = f"""
        📊 ОТЧЕТ О МИГРАЦИИ

        ✅ Успешно:
        - Сохранено сообщений: {saved_messages}
        - Сохранено пользователей: {saved_users}

        💡 Рекомендации:
        - Пользователям, которых не удалось добавить автоматически,
        нужно отправить пригласительные ссылки вручную
    """
    await bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text=report
    )

    # Сохраняем отчет
    migration_status_collection.update_one(
        {"migration_type": "final_report"},
        {"$set": {
            "report": report,
            "statistics": {
                "saved_messages": saved_messages,
                "saved_users": saved_users,
                # "migrated_messages": migrated_messages,
                # "invited_users": invited_users,
                # "failed_messages": len(failed_messages),
                # "failed_invites": len(failed_invites)
            },
            "completed_at": dt.datetime.now()
        }},
        upsert=True
    )
