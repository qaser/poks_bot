import inspect
import logging

from config.bot_config import bot
from config.telegram_config import MY_TELEGRAM_ID


def check_ks(ks):  # проверка на наличие буквы ё
    if ks == 'Приозёрная КС':
        return 'Приозерная КС'
    elif ks == 'Таёжная КС':
        return 'Таежная КС'
    return ks


async def report_error(e: Exception):
    """Уведомляет администратора и логирует ошибку"""
    # Получаем стек вызовов
    frame = inspect.stack()[1]
    func_name = frame.function
    file_name = frame.filename
    line_number = frame.lineno

    # Текст ошибки
    error_text = f"Ошибка в {func_name} ({file_name}, строка {line_number}): {str(e)}"

    # Логируем ошибку в файл
    logging.error(error_text)

    # Пытаемся отправить сообщение админу
    try:
        await bot.send_message(MY_TELEGRAM_ID, text=f'❗️{error_text}')
    except Exception as inner_e:
        logging.error(f"Ошибка при отправке уведомления администратору: {str(inner_e)}")
