import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

import utils.constants as const
from config.bot_config import bot
from config.mail_config import MAIL_LOGIN, MAIL_PASS, PORT, SMTP_MAIL_SERVER
from config.telegram_config import MY_TELEGRAM_ID
from utils.utils import report_error


async def send_email(emails, f_path, user_id=MY_TELEGRAM_ID, ):
    # формируем тело письма
    msg = MIMEMultipart()
    msg["From"] = MAIL_LOGIN
    msg["Subject"] = const.MAIL_SUBJECT
    msg["Date"] = formatdate(localtime=True)
    msg.attach(MIMEText(const.MAIL_TEXT))
    msg["To"] = ', '.join(emails)
    try:
        with open(f_path, 'rb') as f:
            part = MIMEApplication(f.read(), Name=f_path)
            part['Content-Disposition'] = 'attachment; filename="Сводная таблица"'
            msg.attach(part)
    except IOError as e:
        await report_error(e)
    try:
        smtp = smtplib.SMTP(SMTP_MAIL_SERVER, PORT)
        smtp.starttls()
        smtp.ehlo()
        smtp.login(MAIL_LOGIN, MAIL_PASS)
        smtp.sendmail(MAIL_LOGIN, emails, msg.as_string())
        smtp.close()
        await bot.send_message(
            chat_id=user_id,
            text='Письмо успешно отправлено'
        )
    except smtplib.SMTPException as e:
        await report_error(e)
