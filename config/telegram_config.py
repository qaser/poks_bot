import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
MY_TELEGRAM_ID = os.getenv('MY_TELEGRAM_ID')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
BOT_ID = os.getenv('BOT_ID')
API_HASH = os.getenv('API_HASH')
API_ID = os.getenv('API_ID')
TITLE = os.getenv('TITLE')
OTKAZ_GROUP_ID = os.getenv('OTDEL_ID')
NEW_OTKAZ_GROUP = os.getenv('NEW_OTKAZ_GROUP')
EXPLOIT_GROUP_ID = os.getenv('EXPLOIT_GROUP_ID')
SPCH_THREAD_ID = os.getenv('SPCH_THREAD_ID')
