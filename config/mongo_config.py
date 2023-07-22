import pymongo

# Create the client
client = pymongo.MongoClient('localhost', 27017)
db = client['poks_bot_db']
gks_users = db['gks_users']
emergency_stops = db['emergency_stops']
groups = db['groups']
admins = db['admins']
archive = db['archive']
petitions = db['petitions']
buffer = db['buffer']
users = db['users']


'''
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
