import datetime as dt
import pprint
import re

import pymongo
from dateutil.relativedelta import relativedelta

# # Create the client
client = pymongo.MongoClient('localhost', 27017)
db = client['poks_bot_db']
gpa = db['gpa']
emergency_stops = db['emergency_stops']
groups = db['groups']
оperating_time = db['operating_time']
# msgs = db['msgs']

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
    'Приозерная КС',  #
    'Приполярная КС',
    'Пунгинская КС',
    'Пуровская КС',
    'Сорумская КС',
    'Сосновская КС',
    'Сосьвинская КС',
    'Таежная КС',  #
    'Ужгородская КС',
    'Узюм-Юганская КС',
    'Уренгойская КС',
    'Хасырейская КС',
    'Ягельная КС',
    'Ямбургская КС',
]  #  всего 34 шт.

MSGS = [
    'КС Приозерная: Прошу согласовать НО ГПА 84 (СПС-1,35) для вывода в плановое ТО с 01.11.2024 по 08.11.2024. На это период пуск ГПА 82 (СПЧ-1,44).',
    # '«Ново-Пелымская»: ГПА41 - 516 ГПА42 - 521 ГПА 51 - 720 ГПА 52 - 613 ГПА 54 - 550 ГПА 61 - 621 ГПА 62 - 673 ГПА 64 - 621',
    # '«Октябрьская»: ГПА  71 - 645 ГПА  74 - 720 ГПА  81 - 638 ГПА  84 - 720 ГПА  91 - 696 ГПА  94 - 697 ГПА 101 - 113 ГПА 104 - 634',
    # 'КС "Приозёрная": ГПА 24 - 0 ГПА 31 - 0 ГПА 34 - 0 ГПА 51 - 0 ГПА 54 - 0 ГПА 61 - 0 ГПА 64 - 0 ГПА 71 - 0 ГПА 74 - 0 ГПА 84 - 0 ГПА 91 - 0 ГПА 94 - 0',
    # 'КС Верхнеказымская: - ГПА 61 - 257 - ГПА 64 - 257',
    # 'КС Приозерная на проходе, необходимость в пуске ГПА с СПЧ 1,35 по режиму транспорта газа отсутствует',
    # 'КС Ягельная Прошу согласовать ГЗ ГПА-34 после проведения ТО ХС и НО ГПА-32',
    # 'КС «Октябрьская»:-ГПА ст№ 71 - работа; -ГПА ст№ 74 - работа;-ГПА ст№ 81 - работа; -ГПА ст№ 84 - ТО ХС по 07.10.2024;-ГПА ст№ 91 - работа;-ГПА ст№ 94 - работа;-ГПА ст№ 101 - резерв по режиму;-ГПА ст№ 104 - резерв по режиму;',
    # 'КС Карпинская: -ГПА52-резерв (ВТД ТТ КЦ-5 до 29.11.2024) -ГПА54-резерв (ВТД ТТ КЦ-5 до 29.11.2024) -ГПА62-работа -ГПА64 -резерв по режиму (подготовка к ППР КЦ-6 план 02.10.2024-07.10.2024)',
]


def find_gpa():
    gpa_num_find = re.compile(r'№(\d\d|\d\d\d)')
    ks_find = re.compile(r'\w+ая|\w+-\w+ая')
    for msg in MSGS:
        msg = msg.replace(u'\xa0', u' ')
        find_gpa = re.findall('ГПА\s*\d+\s*-\s*\d+', msg)
        print(find_gpa)
        if len(find_gpa) > 0:
            ks = ks_find.search(msg)
            ks = f'{ks.group()} КС' if ks is not None else ''
            ks = check_ks(ks)
            if ks in KS:
                print(ks, find_gpa)
                for agr in find_gpa:
                    num_gpa, work_time = agr.replace(' ', '').split('-')
                    num_gpa = num_gpa[3:]
                    # print(num_gpa, work_time)
                    gpa_instance = gpa.find_one({'ks': ks, 'num_gpa': str(num_gpa)})
                    gpa_id = gpa_instance['_id']
                    gpa.update_one({'_id': gpa_id}, {'$set': {'iskra_comp': True}})
                    date = dt.datetime.now()
                    previous_month = date - relativedelta(months=1)
                    оperating_time.update_one(
                        {'gpa_id': gpa_id},
                        {'$set': {
                            'reg_date': date,
                            'work_time': int(work_time),
                            'month': previous_month.month,
                            'year': previous_month.year,
                        }},
                        upsert=True
                    )

def check_ks(ks):  # проверка на наличие буквы ё
    if ks == 'Приозёрная КС':
        return 'Приозерная КС'
    elif ks == 'Таёжная КС':
        return 'Таежная КС'
    return ks

# find_gpa()

# SPCH = {
#     'Ново-Пелымская КС': [41, 42, 51, 52, 54, 61, 62, 64],
#     'Октябрьская КС': [71, 74, 81, 84, 91, 94, 101, 104],
#     'Карпинская КС': [52, 54, 62, 64],
#     'Правохеттинская КС': [41, 44, 51, 54, 61, 64],
#     'Сосновская КС': [41, 42, 44, 51, 52, 54, 61, 62, 64, 71, 72, 74, 81, 82, 84, 91, 92, 101, 102, 104],
#     'Бобровская КС': [41, 44, 52, 54],
#     'Верхнеказымская КС': [61, 64],
#     'Приозёрная КС': [24, 31, 34, 51, 54, 61, 64, 71, 74, 84, 91, 94],
#     'Лялинская КС': [51, 54],
#     'Ягельная КС': [21, 24, 31, 34, 41, 44, 51, 54, 64, 81, 84, 101, 104],
# }


# pipeline = [
#     {'$match': {'iskra_comp': True}},
#     {'$lookup': {'from': "operating_time", "let": {'id': "$_id"},} },
#     {'$group': {'_id': '$ks', 'gpa_ids': {'$push': {"$toString": "$_id"}}}},
#     {'$setWindowFields': {'sortBy': {'_id': 1}, 'output': {'index': {'$documentNumber': {}}}}},
# ]

pipeline = [
    {'$lookup': {'from': 'operating_time', 'localField': '_id', 'foreignField': 'gpa_id', 'as': 'working_data'}},
    {'$unwind': '$working_data'},
    {'$match': {'working_data.year': 2024, 'working_data.month': 10}},
    {'$group': {'_id': '$ks', 'gpa_ids': {'$push': {"$toString": "$_id"}}}},
    {'$project': {'_id': 0, 'ks': '$_id', 'gpa_ids': 1}},
    {'$sort': {'ks': 1}}
    # {'$setWindowFields': {'sortBy': {'ks': 1}, 'output': {'index': {'$documentNumber': {}}}}},
]

# queryset = gpa.aggregate(pipeline)
# print(list(queryset))


msg = оperating_time.find().limit(1).sort([('$natural',-1)])
print(msg[0])
