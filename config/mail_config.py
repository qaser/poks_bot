import os

from dotenv import load_dotenv

load_dotenv()

MAIL_LOGIN = os.getenv('MAIL_LOGIN')
MAIL_PASS = os.getenv('MAIL_PASS')
SMTP_MAIL_SERVER = os.getenv('SMTP_MAIL_SERVER')
IMAP_MAIL_SERVER = os.getenv('IMAP_MAIL_SERVER')
PORT = os.getenv('PORT')
TO_MAIL = os.getenv('TO_MAIL')
CC_MAIL = os.getenv('CC_MAIL')
CC_MAIL_2 = os.getenv('CC_MAIL_2')
