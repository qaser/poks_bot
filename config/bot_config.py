from aiogram import Bot, Dispatcher
from config.redis_config import storage

from config.telegram_config import TELEGRAM_TOKEN

bot = Bot(
    token=TELEGRAM_TOKEN,
    # protect_content=True,
    parse_mode='HTML'
)
dp = Dispatcher(storage=storage)
