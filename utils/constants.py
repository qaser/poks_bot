import emoji
from datetime import timezone, timedelta


FINISH_EMOJI = emoji.emojize(':green_circle:')
CREATE_EMOJI = emoji.emojize(':white_circle:')
DELETE_EMOJI = emoji.emojize(':black_circle:')
INWORK_EMOJI = emoji.emojize(':yellow_circle:')
REWORK_EMOJI = emoji.emojize(':red_circle:')

BACK_EMOJI = emoji.emojize(':left_arrow:')
EXIT_EMOJI = emoji.emojize(':eject_button:')
DONE_EMOJI = emoji.emojize(':check_mark_button:')
UNDONE_EMOJI = emoji.emojize(':cross_mark:')
DOC_EMOJI = emoji.emojize(':clipboard:')
WASTE_EMOJI = emoji.emojize(':wastebasket:')
EDIT_EMOJI = emoji.emojize(':pencil:')
SEND_EMOJI = emoji.emojize(':envelope:')
SCROLL_EMOJI = emoji.emojize(':scroll:')

KS = [
    'Бобровская КС',
    'Верхнеказымская КС',
    'Ивдельская КС',
    'Казымская КС',
    'Карпинская КС',
    'Комсомольская КС',
    'Краснотурьинская КС',
    'Лонг-Юганская КС',
    'Лялинская КС',
    'Надымская КС',
    'Нижнетуринская КС',
    'Ново-Ивдельская КС',
    'Ново-Пелымская КС',
    'Новокомсомольская КС',
    'Ныдинская КС',
    'Октябрьская КС',
    'Пангодинская КС',
    'Пелымская КС',
    'Перегребненская КС',
    'Правохеттинская КС',
    'Приозерная КС',
    'Приполярная КС',
    'Пунгинская КС',
    'Пуровская КС',
    'Сорумская КС',
    'Сосновская КС',
    'Сосьвинская КС',
    'Таежная КС',
    'Ужгородская КС',
    'Узюм-Юганская КС',
    'Уренгойская КС',
    'Хасырейская КС',
    'Ягельная КС',
    'Ямбургская КС',
]  #  всего 34 шт.

TIME_ZONE = 'Asia/Yekaterinburg'

timezone_offset = +5.0
TZINFO = timezone(timedelta(hours=timezone_offset))

# не делать коды  с нижним подчеркиванием!!!!
DIRECTIONS_CODES = {
    'avia': 'ГПА с авиа. приводом',
    'boat': 'ГПА с судовым приводом',
    'station': 'ГПА со стац. приводом',
    'vtd': 'ВТД',
    'krtt': 'КРТТ, ЗИС',
    'dooks': 'ДООКС',
    'ppr': 'ППР КЦ',
    'rpo': 'РПО',
    'other': 'Общие вопросы',
    'likv': 'Ликвидация',
    'rekon': 'Реконструкция',
    'fond': 'Основные фонды',
    'zra': 'ЗРА',
    'avo': 'АВО газа',
    'gpa': 'Ремонты ГПА',
}

# не делать коды  с нижним подчеркиванием!!!
PROF_USERS = {
    'glav': 'Главный инженер',
    'nachgks': 'Начальник ГКС',
    'znachgks': 'Заместитель начальника ГКС',
    'zamnach': 'Зам. начальника ЛПУМГ по производству',
}

MAIL_SUBJECT = 'Информация о запросах/предложениях/проблемах, полученных телеграм-ботом'

MAIL_TEXT = 'Во вложении находится файл с информацией, собранной ботом за неделю'

TASK_REMINDER = ('Напоминаю о возможности отправить в отдел '
                 'ПОпоЭКС проблемный вопрос.\n'
                 'Для этого выберите в меню соответсвующую команду или нажмите /task')

PETITION_STATUS = {
    'create': ['Создано', 'Создать', CREATE_EMOJI],
    'inwork': ['В работе', 'В работу', INWORK_EMOJI],
    'rework': ['На доработке', 'На доработку', REWORK_EMOJI],
    'delete': ['В архиве (удалено)', 'В архив', DELETE_EMOJI],
    'finish': ['Завершено', 'Завершить', FINISH_EMOJI],
}

PETITION_COLOR = {
    'create': 'FFFFFF',
    'inwork': 'E1CC4F',
    'rework': 'ce8c88',
    'delete': '88bace',
    'finish': 'A0D6B4',
}
