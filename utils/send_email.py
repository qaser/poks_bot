import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.utils import formatdate

import utils.constants as const
from config.telegram_config import MY_TELEGRAM_ID
from config.bot_config import bot
from config.mail_config import (CC_MAIL, MAIL_LOGIN, MAIL_PASS, PORT,
                                SMTP_MAIL_SERVER, TO_MAIL)


async def send_email():
    # формируем тело письма
    msg = MIMEMultipart()
    msg["From"] = MAIL_LOGIN
    msg["Subject"] = const.MAIL_SUBJECT
    msg["Date"] = formatdate(localtime=True)
    msg.attach(MIMEText(const.MAIL_TEXT))
    msg["To"] = ', '.join([TO_MAIL])
    msg["cc"] = ', '.join([CC_MAIL])
    emails = [TO_MAIL] + [CC_MAIL]
    f_path = 'static/tutorial_pdf/Инструкция.pdf'
    try:
        with open(f_path, 'rb') as f:
            part = MIMEApplication(f.read(), Name=f_path)
            part['Content-Disposition'] = 'attachment; filename="Сводная таблица"'
            msg.attach(part)
    except IOError:
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text='Ошибка при открытии файла вложения'
        )
    try:
        smtp = smtplib.SMTP(SMTP_MAIL_SERVER, PORT)
        smtp.starttls()
        smtp.ehlo()
        smtp.login(MAIL_LOGIN, MAIL_PASS)
        smtp.sendmail(MAIL_LOGIN, emails, msg.as_string())
        smtp.close()
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text='Письмо успешно отправлено'
        )
    except smtplib.SMTPException as err:
        await bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=f'Что - то пошло не так...\n\n{err}'
        )
