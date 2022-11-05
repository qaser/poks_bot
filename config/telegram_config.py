import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TEST_CHAT_ID = '-1001555422626'  # тестовый чат
MY_TELEGRAM_ID = os.getenv('MY_TELEGRAM_ID')
