from pyrogram import Client

from config.telegram_config import API_HASH, API_ID, TITLE

app = Client(TITLE, api_id=API_ID, api_hash=API_HASH)
