from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from config.mongo_config import admins


class AdminCheckMiddleware(BaseMiddleware):
    # Команды, доступные всем пользователям, но которые нужно удалять в группах
    PUBLIC_COMMANDS = ['/start', '/reset', '/admin', '/request']

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Пропускаем всё, что не является сообщением
        if not isinstance(event, Message):
            return await handler(event, data)

        # Пропускаем сообщения без текста
        if not event.text:
            return await handler(event, data)

        # Разбиваем текст на части для проверки команды
        parts = event.text.split()
        if not parts:
            return await handler(event, data)

        first_word = parts[0].split('@')[0].lower()

        # Если это не команда - пропускаем
        if not first_word.startswith('/'):
            return await handler(event, data)

        # Проверяем тип чата
        chat_type = event.chat.type if hasattr(event, 'chat') else None

        # Если это публичная группа/супергруппа/канал
        if chat_type in ['group', 'supergroup', 'channel']:
            if first_word in self.PUBLIC_COMMANDS:
                try:
                    await event.delete()
                except:
                    pass
                return
            return await handler(event, data)

        # Для личных сообщений и приватных чатов
        if first_word in self.PUBLIC_COMMANDS:
            return await handler(event, data)

        # Проверяем права для всех остальных команд
        admin = admins.find_one({'user_id': event.from_user.id})
        if not admin:
            try:
                await event.delete()
            except:
                pass
            return

        return await handler(event, data)
