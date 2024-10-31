import asyncio
import os

from dotenv import load_dotenv
from pyrogram import Client

load_dotenv()

API_HASH = os.getenv('API_HASH')
API_ID = os.getenv('API_ID')
TITLE = os.getenv('TITLE')


app = Client(TITLE, api_id=API_ID, api_hash=API_HASH)
