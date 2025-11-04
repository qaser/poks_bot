import datetime as dt
import asyncio

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramRetryAfter

from config.bot_config import bot
from config.mongo_config import users_collection, messages_collection, migration_status_collection
from config.telegram_config import MY_TELEGRAM_ID, NEW_OTKAZ_GROUP, OTKAZ_GROUP_ID
from config.pyrogram_config import app
from utils.utils import report_error

router = Router()


# === ФУНКЦИИ НОРМАЛИЗАЦИИ ===

def normalize_chat_id(chat_id: int) -> int:
    """
    Приводит chat_id к правильному формату.
    Telegram API (Pyrogram/Telethon):
    - супергруппы и каналы должны быть в формате -100XXXXXXXXXX
    - обычные группы могут быть просто -XXXXXXXX
    """
    s = str(chat_id)
    if s.startswith('-') and not s.startswith('-100'):
        return int('-100' + s[1:])
    return int(chat_id)


# Перезаписываем chat_id в нормализованном виде
# OTKAZ_GROUP_ID = normalize_chat_id(OTKAZ_GROUP_ID)
# NEW_OTKAZ_GROUP = normalize_chat_id(NEW_OTKAZ_GROUP)

# === НАСТРОЙКИ ===
USE_PYROGRAM_FOR_INVITES = False  # True = юзер-бот приглашает, False = обычный бот


# ==============================
# Работа с пользователями
# ==============================

async def save_user(user) -> bool:
    """Сохраняет пользователя (aiogram user)"""
    try:
        user_data = {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_bot": user.is_bot,
            "saved_at": dt.datetime.now()
        }
        users_collection.update_one({"user_id": user.id}, {"$set": user_data}, upsert=True)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении пользователя: {e}")
        return False


async def save_user_from_pyrogram(user) -> bool:
    """Сохраняет пользователя из Pyrogram"""
    try:
        user_data = {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_bot": user.is_bot,
            "is_premium": getattr(user, 'is_premium', False),
            "language_code": getattr(user, 'language_code', None),
            "saved_at": dt.datetime.now()
        }
        users_collection.update_one({"user_id": user.id}, {"$set": user_data}, upsert=True)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении пользователя {user.id}: {e}")
        return False


async def get_all_chat_members(chat_id: int):
    """Получает всех участников группы через Pyrogram"""
    members = []
    try:
        print("👥 Начинаем получение списка участников...")
        async for member in app.get_chat_members(chat_id):
            members.append(member)
            if len(members) % 50 == 0:
                await asyncio.sleep(1)
        print(f"✅ Всего получено участников: {len(members)}")
    except Exception as e:
        await report_error(e)
    return members


async def collect_chat_users(chat_id: int):
    """Собирает пользователей из Pyrogram, Aiogram и истории сообщений"""
    users = {}
    saved_count = 0

    # --- 1. Pyrogram (если даст участников) ---
    try:
        async for member in app.get_chat_members(chat_id):
            u = member.user
            users[u.id] = {
                "user_id": u.id,
                "username": u.username,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "is_bot": u.is_bot,
                "source": "pyrogram"
            }
        print(f"👤 Pyrogram нашёл {len(users)} участников")
    except Exception as e:
        print(f"⚠️ Pyrogram не смог получить участников: {e}")

    # --- 2. Aiogram (администраторы) ---
    try:
        admins = await bot.get_chat_administrators(chat_id)
        for admin in admins:
            u = admin.user
            users[u.id] = {
                "user_id": u.id,
                "username": u.username,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "is_bot": u.is_bot,
                "source": "bot_admin"
            }
        print(f"🤖 Aiogram добавил {len(admins)} администраторов")
    except Exception as e:
        print(f"⚠️ Aiogram не смог получить админов: {e}")

    # --- 3. История сообщений (по from_user) ---
    try:
        messages = list(messages_collection.find())
        for m in messages:
            if m.get("user_id"):
                users[m["user_id"]] = {
                    "user_id": m["user_id"],
                    "username": m.get("username"),
                    "first_name": m.get("first_name"),
                    "last_name": m.get("last_name"),
                    "is_bot": False,
                    "source": "messages"
                }
        print(f"💬 Из сообщений добавлено пользователей: {len(users)}")
    except Exception as e:
        print(f"⚠️ Не удалось извлечь юзеров из сообщений: {e}")

    # --- Сохраняем всех в MongoDB ---
    for u in users.values():
        try:
            users_collection.update_one(
                {"user_id": u["user_id"]},
                {"$set": {**u, "saved_at": dt.datetime.now()}},
                upsert=True
            )
            saved_count += 1
        except Exception as e:
            print(f"Ошибка при сохранении {u}: {e}")

    print(f"💾 Сохранено участников в базу: {saved_count}")
    return saved_count



# ==============================
# Работа с сообщениями
# ==============================

async def save_pyrogram_message(message) -> bool:
    """Сохраняет сообщение из Pyrogram в MongoDB"""
    try:
        if not message.text and not message.caption:
            return False

        message_data = {
            "message_id": message.id,
            "chat_id": message.chat.id,
            "user_id": message.from_user.id if message.from_user else None,
            "username": message.from_user.username if message.from_user else None,
            "first_name": message.from_user.first_name if message.from_user else None,
            "text": message.text or message.caption or "",
            "date": message.date,
            "has_media": bool(message.media),
            "saved_at": dt.datetime.now()
        }

        messages_collection.update_one(
            {"message_id": message.id, "chat_id": message.chat.id},
            {"$set": message_data},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Ошибка при сохранении сообщения {message.id}: {e}")
        return False


async def get_all_chat_messages(chat_id: int):
    """Получает все сообщения из чата через Pyrogram"""
    all_messages = []
    try:
        async for message in app.get_chat_history(chat_id, limit=0):  # limit=0 = вся история
            all_messages.append(message)
        print(f"✅ Получено сообщений: {len(all_messages)}")
    except Exception as e:
        await report_error(e)
    return list(reversed(all_messages))  # в хронологическом порядке


async def migrate_messages_to_new_chat():
    """Переносит сохраненные сообщения в новую группу"""
    messages = list(messages_collection.find().sort("date", 1))
    print(f"📤 Начинаем перенос {len(messages)} сообщений")

    failed = []
    success = 0

    for m in messages:
        try:
            text = f"💬 {m['text']}"
            # делим длинные сообщения
            chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]

            for chunk in chunks:
                try:
                    await bot.send_message(chat_id=NEW_OTKAZ_GROUP, text=chunk, disable_notification=True)
                    await asyncio.sleep(1)  # базовая задержка
                except TelegramRetryAfter as e:
                    # если словили FloodWait — ждём указанное время
                    wait_time = int(e.retry_after) + 1
                    print(f"⏳ FloodWait: ждём {wait_time} сек.")
                    await asyncio.sleep(wait_time)
                    # повторяем отправку
                    await bot.send_message(chat_id=NEW_OTKAZ_GROUP, text=chunk, disable_notification=True)

            success += 1
            print(f"Отправлено {success}/{len(messages)}")

        except Exception as e:
            failed.append({"message_id": m["message_id"], "error": str(e)})
            await report_error(e)

    print(f"✅ Успешно: {success}, ошибок: {len(failed)}")
    return success, failed


# ==============================
# Добавление участников
# ==============================

# async def invite_users_with_bot(retry_failed):
#     """Добавляет участников ботом"""
#     failed = []
#     success = 0
#     if retry_failed:
#         last_status = migration_status_collection.find_one(
#             {'migration_type': 'user_invites'},
#             sort=[('processed_at', -1)]
#         )
#         # await bot.send_message(MY_TELEGRAM_ID, last_status)
#         if not last_status or not last_status.get('failed_invites'):
#             return 0, []
#         users = last_status['failed_invites']
#         await bot.send_message(MY_TELEGRAM_ID, f"Повторная рассылка ссылок {len(users)} пользователям")
#     else:
#         users = list(users_collection.find({"is_bot": False}))
#         await bot.send_message(MY_TELEGRAM_ID, f"Первичная рассылка ссылок {len(users)} пользователям")
#     for u in users:
#         uid = u["user_id"]
#         try:
#             link = await bot.create_chat_invite_link(NEW_OTKAZ_GROUP, member_limit=1)
#             try:
#                 await bot.send_message(
#                     chat_id=uid,
#                     text=f'Создана новая группа "ОТКАЗЫ ГПА", прошу присоединиться по ссылке:\n{link.invite_link}'
#                 )
#                 success += 1
#                 await bot.send_message(MY_TELEGRAM_ID, f"ссылка отправлена пользователю {u.get('username')}")
#             except Exception as e:
#                 await report_error(e)
#                 failed.append({"user_id": uid, "username": u.get("username"), "invite_link": link.invite_link})
#         except Exception as e:
#             await report_error(e)
#             failed.append({"user_id": uid, "username": u.get("username"), "error": str(e)})
#         await asyncio.sleep(4)
#     migration_status_collection.update_one(
#         {"migration_type": "user_invites"},
#         {"$set": {"failed_invites": failed, "success_count": success, "processed_at": dt.datetime.now()}},
#         upsert=True
#     )
#     return success, failed


# async def invite_users_with_pyrogram():
#     """Добавляет участников юзер-ботом"""
#     users = list(users_collection.find({"is_bot": False}))
#     failed, success = [], 0
#     for u in users:
#         try:
#             await app.add_chat_members(NEW_OTKAZ_GROUP, [u["user_id"]])
#             success += 1
#             print(f"✅ Добавлен {u['user_id']}")
#         except Exception as e:
#             failed.append({"user_id": u["user_id"], "username": u.get("username"), "error": str(e)})
#         await asyncio.sleep(1)
#     return success, failed


async def check_access():
    """Проверяет доступ к старой и новой группе для бота и юзер-бота"""
    report_lines = ["🔍 Проверка доступа к чатам:\n"]

    # Проверка доступа ботом
    for chat_id, label in [(OTKAZ_GROUP_ID, "Старая группа"), (NEW_OTKAZ_GROUP, "Новая группа")]:
        try:
            chat = await bot.get_chat(chat_id)
            report_lines.append(f"🤖 Бот: ✅ доступ к {label} — {chat.title}")
        except Exception as e:
            report_lines.append(f"🤖 Бот: ❌ нет доступа к {label} — {e}")

    # Проверка доступа юзер-ботом (Pyrogram)
    for chat_id, label in [(OTKAZ_GROUP_ID, "Старая группа"), (NEW_OTKAZ_GROUP, "Новая группа")]:
        try:
            chat = await app.get_chat(chat_id)
            report_lines.append(f"👤 Юзер-бот: ✅ доступ к {label} — {chat.title}")
        except Exception as e:
            report_lines.append(f"👤 Юзер-бот: ❌ нет доступа к {label} — {e}")

    report_text = "\n".join(report_lines)
    await bot.send_message(MY_TELEGRAM_ID, report_text)
    return report_text


# ==============================
# Полная миграция
# ==============================

@router.message(Command("migrate"))
async def complete_migration(message: Message):
    messages_collection.delete_many({})
    # users_collection.delete_many({})
    await bot.send_message(MY_TELEGRAM_ID, "🚀 Начинаем миграцию...")
    access_report = await check_access()

    # Если нет доступа к старой или новой группе — останавливаемся
    if "❌" in access_report:
        await bot.send_message(MY_TELEGRAM_ID, "⚠️ Миграция остановлена: нет доступа к одной из групп.")
        return
    try:
        # 1. Сохраняем историю сообщений
        all_messages = await get_all_chat_messages(OTKAZ_GROUP_ID)
        saved_msgs = 0
        for m in all_messages:
            if await save_pyrogram_message(m):
                saved_msgs += 1

        # 2. Сохраняем участников
        # saved_users = await collect_chat_users(OTKAZ_GROUP_ID)

        # # 3. Переносим сообщения в новую группу
        migrated, failed_msgs = await migrate_messages_to_new_chat()

        # 5. Отчет
        report = f"""
        📊 ОТЧЕТ О МИГРАЦИИ

        ✅ Сообщений получено: {len(all_messages)}
        💾 Сообщений сохранено: {saved_msgs}

        📤 Сообщений перенесено: {migrated}, ошибок: {len(failed_msgs)}

        """

        await bot.send_message(MY_TELEGRAM_ID, report)

    except Exception as e:
        await report_error(e)


# @router.message(Command("invite_users"))
# async def users_invite(message: Message):
#     await bot.send_message(MY_TELEGRAM_ID, "🚀 Начинаем приглашение пользователей")
#     # access_report = await check_access()

#     # Если нет доступа к старой или новой группе — останавливаемся
#     # if "❌" in access_report:
#     #     await bot.send_message(MY_TELEGRAM_ID, "⚠️ Миграция остановлена: нет доступа к одной из групп.")
#         # return
#     try:
#         # # 4. Добавляем участников
#         # if USE_PYROGRAM_FOR_INVITES:
#         #     invited, failed_invites = await invite_users_with_pyrogram()
#         # else:
#         invited, failed_invites = await invite_users_with_bot(True)

#         # 5. Отчет
#         report = f"""
#         📊 ОТЧЕТ О МИГРАЦИИ

#         ➕ Пользователей добавлено: {invited}, ошибок: {len(failed_invites)}
#         """

#         await bot.send_message(MY_TELEGRAM_ID, report)

#     except Exception as e:
#         await report_error(e)
