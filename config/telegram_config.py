import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
MY_TELEGRAM_ID = os.getenv('MY_TELEGRAM_ID')
BOT_ID = os.getenv('BOT_ID')
API_HASH = os.getenv('API_HASH')
API_ID = os.getenv('API_ID')
TITLE = os.getenv('TITLE')
