import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from config.bot_config import bot
from config.mail_config import MAIL_LOGIN, MAIL_PASS, PORT, SMTP_MAIL_SERVER
from config.telegram_config import MY_TELEGRAM_ID


# backup_dir = f'C:\Dev\poks_bot\\var\\backups\mongobackups\\22-08-23\poks_bot_db'

async def send_backups(emails, db_name, backup_path):
    # cur_date = dt.datetime.now().strftime('%d-%m-%y')
    # backup_dir = f'../../../var/backups/mongobackups/{cur_date}/poks_bot_db'
    # формируем тело письма
    topic = f'Архивы БД {db_name}'
    msg = MIMEMultipart()
    msg["From"] = MAIL_LOGIN
    msg["Subject"] = topic
    msg["Date"] = formatdate(localtime=True)
    msg.attach(MIMEText(topic))
    msg["To"] = ', '.join(emails)
    try:
        for d in os.listdir(backup_path):
            f_path = f'{backup_path}\{d}'
            with open(d, 'rb') as f:
                part = MIMEApplication(f.read(), Name=f_path)
                part['Content-Disposition'] = 'attachment; filename="Сводная таблица"'
                msg.attach(part)
    except IOError as err:
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=f'Ошибка при открытии файла вложения: {err}'
        )
    try:
        smtp = smtplib.SMTP(SMTP_MAIL_SERVER, PORT)
        smtp.starttls()
        smtp.ehlo()
        smtp.login(MAIL_LOGIN, MAIL_PASS)
        smtp.sendmail(MAIL_LOGIN, emails, msg.as_string())
        smtp.close()
    except smtplib.SMTPException as e:
        print(e)
