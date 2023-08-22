import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from config.bot_config import bot
from config.mail_config import MAIL_LOGIN, MAIL_PASS, PORT, SMTP_MAIL_SERVER
from config.telegram_config import MY_TELEGRAM_ID


async def send_dbs_mail(emails, db_name, backup_path):
    # формируем тело письма
    topic = f'Архивы БД {db_name}'
    msg = MIMEMultipart()
    msg["From"] = MAIL_LOGIN
    msg["Subject"] = topic
    msg["Date"] = formatdate(localtime=True)
    msg.attach(MIMEText(topic))
    msg["To"] = ', '.join(emails)
    try:
        for file in os.listdir(backup_path):
            # f_path = f'{backup_path}\{file}'
            f_path = f'{backup_path}/{file}'
            with open(f_path, 'rb') as f:
                part = MIMEApplication(f.read(), Name=f_path)
                part['Content-Disposition'] = f'attachment; filename="{file}"'
                msg.attach(part)
    except IOError as err:
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=f'Ошибка при открытии файла вложения: {err}\n\n{f_path}\n{file}'
        )
    try:
        smtp = smtplib.SMTP(SMTP_MAIL_SERVER, PORT)
        smtp.starttls()
        smtp.ehlo()
        smtp.login(MAIL_LOGIN, MAIL_PASS)
        smtp.sendmail(MAIL_LOGIN, emails, msg.as_string())
        smtp.close()
    except smtplib.SMTPException as e:
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=f'Ошибка при отправке почты: {err}'
        )
