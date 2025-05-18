import pymongo

# Create the client
client = pymongo.MongoClient('localhost', 27017)
db = client['poks_bot_db']
emergency_stops = db['emergency_stops']
groups = db['groups']
admins = db['admins']
archive = db['archive']
petitions = db['petitions']
buffer = db['buffer']
users = db['users']
bugs = db['bugs']
docs = db['docs']
bounces = db['bounces']
equip = db['equip']
gpa = db['gpa']
giga_chats = db['giga_chats']
msgs = db['msgs']
operating_time = db['operating_time']
otkaz_msgs = db['otkaz_msgs']
paths = db['paths']
reqs = db['requests']
req_counter = db['req_counter']


'''
paths {
    path_type: ['Стационар_1', 'Стационар_2', 'Авиа', 'Судовые']
    num_stages: 3,
    stages {
        '1': id_admin,
        '2': id_admin,
        '3': id_admin
    }
}

reqs {
    req_type: [with_approval, without_approval]
    author_id: user_id,
    ks: станция,
    gpa_id: gpa_id,
    num_gpa: номер гпа
    datetime: datetime,
    text: text
    path_id: path_id,
    status: [inwork, approved, rejected]
    reject_reason: причина отклонения
    current_stage: 2,
    request_datetime: datetime, - дата на которую делается запрос
    notification_datetime: datetime - время отправки уведомления о успешности пуска ГПА
    is_complete: False/True  -  при полном завершении цикла от заявки до пуска
    is_fail: False/True - удачен пуск или нет
    fail_reason: причина неудавшегося пуска
    stages {
        '1': {
            datatime: datetime,
            major_id: admin_id,
            status: [pass, reject, apply, inwork]
        }
        '2': {
            datatime: datetime,
            major_id: admin_id,
            status: [pass, reject, apply, inwork]
        }
    }
}


структура данных ELECTRICS
    'class_code': код класса
    'class_of': класс оборудования
    'type_code': шифр оборудования
    'type_of': вид оборудования
    'part_code': шифр узла
    'part_of': наименование узла
    'cipher': шифр оборудования согласно СТО 1011

структура данных REASONS
    'group_code': код группы причин
    'group': группа причин
    'reason_code': код причины
    'reason': причина отказа
    'cipher': код причины отказа согласно СТО 1011

структура данных ОТКАЗОВ
    'type_of': тип отказа
    'code': шифр отказа
    'description': описание (характер) отказа

структура данных группы
    '_id': id telegram-группы
    'group_name': название группы
    'sub_banned': '',  # этот флаг нужен для отмены рассылки напоминаний

структура данных пользователя
    '_id': название компрессорной станции
    'glav_ing': {
        'user_id': id пользователя телеграм
        'username':  имя пользователя
    }
    'nach_gks': {
        'user_id': id пользователя телеграм
        'username':  имя пользователя
    }
    'zam_nach_gks': {
        'user_id': id пользователя телеграм
        'username':  имя пользователя
    }

структура данных аварийных остановов
    '_id': дефолтный первичный ключ
    'date': дата ввода данных об АО
    'station': название станции
    'gpa': номер ГПА

структура данных администраторов
    '_id': дефолтный первичный ключ
    'user_id' id пользователя телеграм
    'username': имя пользователя
'''
