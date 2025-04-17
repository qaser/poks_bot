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
        if not isinstance(event, Message):
            return await handler(event, data)
        if not event.text:
            return await handler(event, data)
        command_parts = event.text.split()
        if not command_parts:
            return await handler(event, data)
        command = command_parts[0].split('@')[0].lower()
        if command in self.PUBLIC_COMMANDS:
            return await handler(event, data)
        admin = admins.find_one({'user_id': event.from_user.id})
        if not admin:
            return
        return await handler(event, data)
