INITIAL_TEXT = (
    'Вы инициировали возможность бота отправлять Вам сообщения.\n'
    'Если Вы являетесь начальником ГКС нажмите /gks'
)

NEW_GROUP_TEXT = (
    'Для выполнения ботом своих функций Вам необходимо предоставить ему права администратора.\n\n'
    'Для просмотра информации по порядку расследования произошедшего отказа '
    'нажмите /manual\n\n'
)

HELP_TEXT = (
    'Для внесения данных о начальнике ГКС (выполняется лично пользователем) нажмите /gks\n\n'
    'Для отправки инструкций по созданию рабочего чата нажмите /ao\n\n'
    'Для просмотра списка зарегистрированных пользователей нажмите /users\n\n'
    'Для сброса настроек клавиатуры и отмены текущего действия нажмите /reset\n\n'
    'Для отмены рассылки уведомлений (для группы) нажмите /unsub\n\n'
    'Для включения рассылки уведомлений (для группы) нажмите /sub\n\n'
    'Для просмотра инструкции по расследованию отказа нажмите /manual'
)

MANUAL = (
    'В рамках расследования произошедшего отказа необходимо:\n\n'
    '1. Сразу после отказа (в течение <b>30 минут</b>) и получения оперативной информации об отказе от сменного персонала, анализе трендов и осмотре ГПА (при необходимости) предоставить в группу сообщение в следующей форме:\n\n'
    '<i>«При работе ГПА на режиме Магистраль произошёл АО с расшифровкой в САУ ГПА  «_».\nПри осмотре ГПА обнаружено _.\nПри анализе трендов отмечено _. (и другие оперативно выявленные причины и факторы).\nВедётся расследование. Для восстановления режима ТТР ГТС выполнен пуск ГПА ст.№_ за __час(ов)__минут.»</i>\n\n'
    '2. В течение <b>2</b> рабочих часов направить в группу подписанное оперативное донесение об отказе.\n\n'
    '3. В течение <b>4</b> рабочих часов направить в группу:\n\n'
    '  - тренды, события, хронология отказа, фото повреждённых (отказавших) узлов;\n\n'
    '  - скан-копии объяснительных персонала, непосредственно участвовавшего в событиях, связанных с отказом (сменный персонал - обязательно, персонал АиМО и ЭВС - в случае необходимости).\n\n'
    '4. В течении первых <b>4-х</b> часов после отказа предоставить в группу план мероприятий (технологическую карту) по расследованию отказа с распределением по направлениям деятельности ГКС, АиМО, ЭВС (как пример: подшипники не разбираются, пока не проверено оборудование АиМО, если был резкий заброс или нестабильные показания параметра по трендам).\n\n'
    '5. <b>Ежедневно</b> направлять информацию о выполненных работах, выявленных неисправностях с фотоотчётом о выполнении этапов работ, а также план работ на следующий день.\n\n'
    '6. При установлении причины отказа четко определить причинно-следственную связь между выявленными неисправностями и внешними проявлениями отказа.\n\n'
    '7. Причину и мероприятия по недопущению подобных отказов предварительно направить в группу для согласования специалистом по направлению деятельности и заместителем начальника ПОпоКС.\n\n'
    '8. В течение <b>2-х</b> календарных дней предоставить в группу акт расследования отказа установленной формы, содержащий причины отказа, предпосылки возникновения отказа и факторы, способствующие развитию отказа, а также перечень проработанных мероприятий по недопущению повторных отказов.\n\n'
    '9. Обеспечить оперативное исполнение указаний специалистов ПОпоКС, направленных на определение причин отказа.\n\n'
    '10. Обеспечить оперативное устранение замечаний специалистов ПОпоКС к представляемым материалам расследования.\n\n'
    '11. Продление расследования осуществлять в соответствии с требованиями п.8.12 Положения-ИТЦ-1551-2021.'
)

REMAINDER = (
    'Прошу предоставить информацию о выполненных работах, '
    'выявленных неисправностях с фотоотчётом, '
    'а также план работ на следующий день.'
)

REPORT = (
    'При работе ГПА на режиме Магистраль произошёл АО с расшифровкой в САУ ГПА "_". '
    'При осмотре ГПА обнаружено _. При анализе трендов отмечено _. '
    '(и другие оперативно выявленные причины и факторы). Ведётся расследование. '
    'Для восстановления режима ТТР ГТС выполнен пуск ГПА ст.№_ за __час(ов)__минут.'
)