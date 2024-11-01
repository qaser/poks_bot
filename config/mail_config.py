import os

from dotenv import load_dotenv

load_dotenv()

MAIL_LOGIN = os.getenv('MAIL_LOGIN')
MAIL_PASS = os.getenv('MAIL_PASS')
SMTP_MAIL_SERVER = os.getenv('SMTP_MAIL_SERVER')
IMAP_MAIL_SERVER = os.getenv('IMAP_MAIL_SERVER')
PORT = os.getenv('PORT')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
SPCH_REPORT_MAIL = os.getenv('SPCH_REPORT_MAIL')
