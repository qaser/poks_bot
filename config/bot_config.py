from aiogram import Bot, Dispatcher

from config.redis_config import storage
from config.telegram_config import TELEGRAM_TOKEN
from middlewares.admin_check import AdminCheckMiddleware


bot = Bot(token=TELEGRAM_TOKEN, parse_mode='HTML')
dp = Dispatcher(storage=storage)
