from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from typing import Callable, Dict, Any, Awaitable
from datetime import datetime
from config.mongo_config import admins


class AdminCheckMiddleware(BaseMiddleware):
    # Команды, доступные всем пользователям
    PUBLIC_COMMANDS = ['/start', '/reset', '/admin']

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Пропускаем всё, что не является сообщением
        if not isinstance(event, Message):
            return await handler(event, data)

        # Пропускаем сообщения без текста (фото, документы и т.д.)
        if not event.text:
            return await handler(event, data)

        # Разбиваем текст на части для проверки команды
        parts = event.text.split()
        if not parts:  # На всякий случай, если пустой текст
            return await handler(event, data)

        first_word = parts[0].split('@')[0].lower()  # Убираем mention бота если есть

        # Если это не команда (не начинается с /) - пропускаем
        if not first_word.startswith('/'):
            return await handler(event, data)

        # Если это публичная команда - пропускаем
        if first_word in self.PUBLIC_COMMANDS:
            return await handler(event, data)

        # Проверяем права для всех остальных команд
        admin = admins.find_one({'user_id': event.from_user.id})
        if not admin:
            return

        return await handler(event, data)
