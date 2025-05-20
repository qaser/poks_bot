import datetime as dt
import pprint
import re

import pymongo

# # Create the client
client = pymongo.MongoClient('localhost', 27017)
db = client['poks_bot_db']
gpa = db['gpa']
emergency_stops = db['emergency_stops']
groups = db['groups']
reqs = db['requests']
req_counter = db['req_counter']
# msgs = db['msgs']

GROUP_NAMES = [
    "Верхнеказымское ЛПУМГ АО ГПА-Ц-16 ст. №93 29.03.2023",
    "Лялинская КС ст. №63, ГТК-25ИР, АО, 16.03.2023",
    "КС Ямбургская - 11 ГПА-Ц-16 АО 17.04.2023"
    "Пуровская-15 ГТК-10И АО 24.01.2023",
    "Приозерная-51 ГПА-Ц-16 АО 21.01.2023",
    "Пелымская-63 ГТК-25ИР АО 27.12.2022",
    "КС Краснотурьинская АО ГПА 91 ГТК-25И 03.12.22",
    "Бобровская-52 ГПА-Ц-16 АО 29.11.2022",
    "Сосновское ЛПУМГ- ГПА-Ц-16 ст.N 104 АО 16.11.2023",
    "КС Уренгойская-34 ГПА-12Р Урал, АО 15.11.2022",
    "КС Лялинская ГТК-25И(Р) ст.N33 АО 08.08.2023 23:20",
    '27.10.24 19:59 Сосновское ЛПУМГ АО ГПА ст.№104 «Помпаж Д»'
]

MSGS = [
    '27.10.24 19:59 Сосновское ЛПУМГ АО ГПА ст.№104 «Помпаж Д»',
    'Пангодинское ЛПУМГ, КС Пангодинская 15:11 АО ГПА №64 – «отсутствие факела»',
    '11.09.2024 19:20 Краснотурьинское ЛПУМГ ГПА №44 АО – рассогласование положения ТРК.',
    '02.09.2024 03:28 Октябрьское ЛПУМГ АО ГПА-Ц-16, ст. №52 – помпаж нагнетателя.',
    '01.09.2024 06:02 Нижнетуринское ЛПУМГ КС Лялинская АО ГПА №44 – «ЭОР ротора СТ».',
    '31.08.2024 11:38 Лонг-Юганское ЛПУМГ АО ГПА 46 – алгоритм противопомпажной защиты нагнетателя.',
    '31.08.2024 01:55 Краснотурьинское ЛПУМГ ГПА ст.№43 АО отсутствует питание САУ ГПА',
    '24.08.2024 21:15 Нижнетуринское ЛПУМГ Лялинская КС АО ГПА №28 – Низкое давление масла смазки ЦБН',
    '05.08.24 Нижнетуринское ЛПУМГ, КС Лялинская, ГПА№52 в 16:00 ВНО - вибрация нагнетателя (ЗОН).',
    '02.08.2024 18:20  КС Новопелымская, АО ГПА ст. №24 с расшифровкой «Высокая температура на выхлопе».',
    '25.07.2024 04:34 Ныдинское ЛПУМГ ГПА №33 АО – высокая температура масла задней опоры двигателя.',
    '09.07.2024 11:54 Комсмольское ЛПУМГ КС Ново-Комосомольская (КС-20) ГПА ст. №72, ОП – «t газа за ТНД (точка 13) < Т тнд ср - 200C»',
    '09.07.2024 Пелымское ЛПУМГ КС Пелымская ГПА ст. №55, ОП – «Обратная вспышка в камере сгорания»',
    '01.07.2024 11:07 Комсомольское , КС-11  АО ГПА №13 «Аварийные обороты ТНД». Дана команда на пуск резервного ГПА.',
    '21.06.2024 14:02 Нижнетуринское ЛПУМГ, КС Лялинская, ГПА ст.№51 (1 приоритет), АО - «Вибрация нагнетателя»',
    '12.06.2024 1:43 Нижнетуринское ЛПУМГ, КС Лялинская, ГПА ст.№33 (1 приоритет), АО - "Погасание факела"',
    'Правохеттинское ЛПУМГ, ГПА№92 (1 приоритет), в 7:45 АО - помпаж двигателя.',
    'Правохеттинское ЛПУМГ, ГПА№64, в 1:50 АО - помпаж двигателя (ложное).',
]

# req_count = reqs.count_documents({})
# queryset = list(reqs.find({}))
# req_counter.insert_one({
#     '_id': 'request_id',
#     'seq': req_count
# })
# for num, req in enumerate(queryset):
#     reqs.update_one(
#         {'_id': req['_id']},
#         {'$set': {'req_num': num+1}}
#     )

# for msg in MSGS:
#     date_find = re.compile(r'\d\d\.\d\d\.(\d\d\d\d|\d\d)')
#     time_find = re.compile(r'(\d|\d\d)\:\d\d')
#     try:
#         date_text = date_find.search(msg).group()
#         time_text = time_find.search(msg).group()
#     except:
#         pass
#     try:
#         result = re.sub(date_text, f'<b><u>{date_text}</u></b>', msg)
#     except:
#         pass
#     try:
#         result = re.sub(time_text, f'<b><u>{time_text}</u></b>', result)
#     except:
#         pass
#     print(result)

# def find_gpa():
#     gpa_num_find = re.compile(r'№(\d*)')
#     date_find = re.compile(r'\d\d\.\d\d\.(\d\d\d\d|\d\d)')
#     lpu_find = re.compile(r'\w+ое\sЛПУМГ|\w+-\w+ое\sЛПУМГ')
#     ks_find = re.compile(r'\w+ая|\w+ая')
#     for msg in MSGS:
#         date = date_find.search(msg)
#         num_gpa = gpa_num_find.search(msg)
#         lpu = lpu_find.search(msg)
#         ks = ks_find.search(msg)
#         try:
#             lpu_name = lpu.group()
#         except AttributeError:
#             lpu_name = None
#         try:
#             ks = f'{ks.group()} КС'
#         except AttributeError:
#             ks = None
#         try:
#             day, month, year = date.group().split('.')
#             year = f'20{year}' if len(year) == 2 else year
#             date = f'{day}.{month}.{year}'
#         except AttributeError:
#             date = dt.datetime.now().strftime('%d.%m.%Y')
#         try:
#             num_gpa = num_gpa.group()
#         except AttributeError:
#             num_gpa = None
#         if lpu_name is not None and num_gpa is not None:
#             queryset = list(gpa.find({'lpu': lpu_name, 'num_gpa': num_gpa[1:]}))
#             print(lpu_name, num_gpa, ks)
#             if len(queryset) > 1 and ks is not None:
#                 gpa_instance = gpa.find_one({'lpu': lpu_name, 'num_gpa': num_gpa[1:], 'ks': ks})
#                 if gpa_instance is not None:
#                     print('создаем группу 1 уточненно')
#                     continue
#             elif len(queryset) == 1:
#                 print('создаем группу 1')
#                 continue
#             else:
#                 print('ручное создание группы 1')
#                 continue
#         elif ks is not None and num_gpa is not None:
#             gpa_instance = gpa.find_one({'ks': ks, 'num_gpa': num_gpa[1:]})
#             if gpa_instance is not None:
#                 print('создаем группу 2')
#                 continue
#             else:
#                 print('ручное создание группы 2')
#                 continue
#         else:
#             print('ручное создание группы 2')
#             continue

# find_gpa()

# date_reg = re.compile(r'\d\d\.\d\d\.(\d\d\d\d|\d\d)')

# for group in GROUP_NAMES:
#     date = date_reg.search(group)
#     day, month, year = date.group().split('.')
#     year = f'20{year}' if len(year) == 2 else year
#     date = f'{day}.{month}.{year}'
#     print(date)


# pipeline = [
#     {'$match': {'ao': {'$exists': 'true'}}},
#     {'$project': {
#         'name_gpa': 1,
#         'numberOfAO': {
#             '$cond': {
#                 'if': {'$isArray': "$ao"},
#                 'then': { '$size': "$ao" },
#                 'else': "NA"
#             }
#         }
#     }
#     },
#     {'$group': {'_id': '$name_gpa', 'count': {'$sum': '$numberOfAO'}}}
# ]

# qs = gpa.aggregate(pipeline)
# pprint.pprint(list(qs))


# def pop_aos():
#     gpa.update_many(
#         {},
#         {'$set': {'ao': []}}
#     )
#     qs = list(emergency_stops.find({}))
#     count = 0
#     for ao in qs:
#         gpa_inst = gpa.find_one({'ks': ao.get('station'), 'num_gpa': ao.get('gpa')})
#         if gpa_inst is not None:
#             ao_list = gpa_inst.get('ao')
#             ao_list.append(ao.get('_id'))
#             gpa.update_one(
#                 {'ks': ao.get('station'), 'num_gpa': ao.get('gpa')},
#                 {'$set': {'ao': ao_list}}
#             )
#             count += 1
#         else:
#             continue
#     print(count)

# pop_aos()

# queryset = list(msgs.find({}))
# print(queryset)
