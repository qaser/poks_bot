import os

from dotenv import load_dotenv

load_dotenv()

MAIL_LOGIN = os.getenv('MAIL_LOGIN')
MAIL_PASS = os.getenv('MAIL_PASS')
MAIL_SERVER = os.getenv('MAIL_SERVER')
