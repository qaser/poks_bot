import emoji
from datetime import timezone, timedelta


GREEN_EMOJI = emoji.emojize(':green_circle:')
RED_EMOJI = emoji.emojize(':red_circle:')
BACK_EMOJI = emoji.emojize(':left_arrow:')
EXIT_EMOJI = emoji.emojize(':eject_button:')
DONE_EMOJI = emoji.emojize(':check_mark_button:')
UNDONE_EMOJI = emoji.emojize(':cross_mark:')
DOC_EMOJI = emoji.emojize(':clipboard:')
DELETE_EMOJI = emoji.emojize(':wastebasket:')

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
    'avia': 'ГПА с авиа.приводом',
    'boat': 'ГПА с судовым приводом',
    'station': 'ГПА со стационарным приводом',
    'vtd': 'ВТД',
    'krtt': 'КРТТ, ЗИС',
    'dooks': 'ДООКС',
    'ppr': 'ППР КЦ',
    'rpo': 'РПО',
    'other': 'Общие вопросы',
}

# не делать коды  с нижним подчеркиванием!!!
PROF_USERS = {
    'glav': 'Главный инженер',
    'nachgks': 'Начальник ГКС',
    'znachgks': 'Заместитель начальника ГКС',
}
