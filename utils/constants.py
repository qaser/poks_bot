from datetime import timedelta, timezone

import emoji

NEXT_BUTTON = 'Продолжить 🔜'
BACK_BUTTON = '🔙 Назад'
EXIT_BUTTON = '🔚 Выход'

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
SCROLL_EMOJI = emoji.emojize(':orange_book:')
GROUP_EMOJI = emoji.emojize(':closed_mailbox_with_raised_flag:')
SORT_EMOJI = emoji.emojize(':chart_increasing:')

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

# не делать коды с нижним подчеркиванием!!!
PROF_USERS = {
    'glav': 'Главный инженер',
    'nachgks': 'Начальник ГКС',
    'znachgks': 'Заместитель начальника ГКС',
    'zamnach': 'Зам. начальника ЛПУМГ по производству',
}

MAIL_SUBJECT = 'Информация полученная телеграм-ботом'

MAIL_TEXT = 'Во вложении находится файл с информацией, собранной ботом по Вашему запросу'

TASK_REMINDER = ('Напоминаю о возможности отправить в отдел '
                 'ПОЭКС проблемный вопрос.\n'
                 'Для этого выберите в меню соответствующую команду или нажмите /task')

GROUP_REMAINDER = (
    'Прошу предоставить информацию о выполненных работах, '
    'выявленных неисправностях с фотоотчётом, '
    'а также план работ на следующий день.'
)

PETITION_STATUS = {
    'create': ['Создано', 'Создать', CREATE_EMOJI],
    'inwork': ['В работе', 'В работу', INWORK_EMOJI],
    'rework': ['На доработке', 'На доработку', REWORK_EMOJI],
    'delete': ['В архиве', 'В архив', DELETE_EMOJI],
    'finish': ['Завершено', 'Завершить', FINISH_EMOJI],
}

PETITION_COLOR = {
    'create': 'FFFFFF',
    'inwork': 'E1CC4F',
    'rework': 'ce8c88',
    'delete': '88bace',
    'finish': 'A0D6B4',
}

INITIAL_TEXT = (
    'Вы активировали возможность бота отправлять Вам сообщения.\n'
    'Для прохождения процедуры регистрации нажмите /registration'
)

NEW_GROUP_TEXT = (
    'Сообщение с инструкцией по расследованию отказа закреплено в "шапке" чата'
)

GROUPS_GPA = 'Ссылки на группы с прошлыми расследованиями отказов этого ГПА:'

HELP_ADMIN = (
    'Изменение своей учетной записи /admin\n\n'
    'Просмотр администраторов /admins\n\n'
    # 'Просмотр пользователей /users\n\n'
    # 'Просмотр текущих задач /review\n\n'
    'Выгрузка текущих задач на почту /mail\n\n'
    # 'Просмотр статистики АО(ВНО) /stats\n\n'
    # 'Отправка инструкций по созданию рабочего чата /ao\n\n'
    'Автоматическое создание рабочего чата /ao\n\n'
    'Отмена рассылки уведомлений (для группы) /unsub\n\n'
    'Включение рассылки уведомлений (для группы) /sub\n\n'
    'Временное отключение защиты от копирования (для группы) /copy\n\n'
    # 'Отправка сообщения об ошибке /bugs'
)

HELP_USER = (
    'Изменение регистрационных данных /registration\n\n'
    # 'Просмотр текущих задач\вопросов\проблем /review\n\n'
    # 'Новая задача\вопрос\проблема /task\n\n'
    # 'Отправка сообщения об ошибке /bugs'
)

MANUAL = (
    'В рамках расследования произошедшего отказа необходимо:\n\n'
    '1. Сразу после отказа <b>(в течение 30 минут)</b> и получения оперативной '
    'информации об отказе от сменного персонала, анализе трендов и осмотре '
    'ГПА (при необходимости) предоставить в группу сообщение в следующей форме:\n\n'
    '<i>«При работе ГПА на режиме Магистраль произошёл АО с расшифровкой в САУ ГПА «__».\n'
    'При осмотре ГПА обнаружено ____.\nПри анализе трендов отмечено ____.\n'
    '(и другие оперативно выявленные причины и факторы).\nВедётся расследование.\n'
    ' Для восстановления режима ТТР ГТС выполнен пуск ГПА ст.№_ за __час(ов)__минут.»</i>\n\n'
    ' 2. В течение <b>2-х рабочих часов</b> направить в группу подписанное оперативное '
    'донесение об отказе, а также на почту всех специалистов по ГПА, зам.начальника '
    'ПОЭКС и ИТЦ (Волегов А.Л.) (подписанное и в редактируемом формате оперативное '
    'донесение об отказе).\n\n'
    ' 3. В течении первых <b>4-х часов после отказа</b> предоставить в группу план мероприятий '
    '(технологическую карту) по расследованию отказа с распределением по направлениям '
    'деятельности ГКС, АиМО, ЭВС (как пример: подшипники не разбираются, пока не проверено '
    'оборудование АиМО, если был резкий заброс или нестабильные показания параметра по трендам);\n'
    '- тренды, события, хронология отказа, фото повреждённых (отказавших) узлов.\n\n'
    '4. <u>Ежедневно</u> направлять информацию о выполненных работах, выявленных неисправностях '
    'с фотоотчётом о выполнении этапов работ, а также план работ на следующий день.\n\n'
    '5. При установлении причины отказа четко определить причинно-следственную связь между '
    'выявленными неисправностями и внешними проявлениями отказа.\n\n'
    '6. В течение <b>2-х календарных дней</b> предоставить в группу акт расследования отказа установленной формы.\n\n'
    '7. Обеспечить оперативное исполнение указаний специалистов производственных отделов и руководителей, '
    'направленных на определение причин отказа.\n\n'
    '8. Обеспечить оперативное устранение замечаний специалистов производственных отделов и руководителей '
    'к представляемым материалам расследования.\n\n'
    '9. Продление сроков расследования осуществлять в соответствии с требованиями <u>п.8.12</u> <b>Положения-ИТЦ-1551-2021.</b>'
)

REPORT = (
    'При работе ГПА на режиме Магистраль произошёл АО с расшифровкой в САУ ГПА "_". '
    'При осмотре ГПА обнаружено _. При анализе трендов отмечено _. '
    '(и другие оперативно выявленные причины и факторы). Ведётся расследование. '
    'Для восстановления режима ТТР ГТС выполнен пуск ГПА ст.№_ за __час(ов)__минут.'
)

MONTHS_NAMES = {
    '1': 'январь',
    '2': 'февраль',
    '3': 'март',
    '4': 'апрель',
    '5': 'май',
    '6': 'июнь',
    '7': 'июль',
    '8': 'август',
    '9': 'сентябрь',
    '10': 'октябрь',
    '11': 'ноябрь',
    '12': 'декабрь'
}
