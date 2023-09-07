# import re

# GROUP_NAMES = [
#     "Верхнеказымское ЛПУМГ АО ГПА-Ц-16 ст. №93 29.03.2023",
#     "Лялинская КС ст. №63, ГТК-25ИР, АО, 16.03.2023",
#     "КС Ямбургская - 11 ГПА-Ц-16 АО 17.04.2023"
#     "Пуровская-15 ГТК-10И АО 24.01.2023",
#     "Приозерная-51 ГПА-Ц-16 АО 21.01.2023",
#     "Пелымская-63 ГТК-25ИР АО 27.12.2022",
#     "КС Краснотурьинская АО ГПА 91 ГТК-25И 03.12.22",
#     "Бобровская-52 ГПА-Ц-16 АО 29.11.2022",
#     "Сосновское ЛПУМГ- ГПА-Ц-16 ст.N 104 АО 16.11.2023",
#     "КС Уренгойская-34 ГПА-12Р Урал, АО 15.11.2022",
#     "КС Лялинская ГТК-25И(Р) ст.N33 АО 08.08.2023 23:20"
# ]

# date_reg = re.compile(r'\d\d\.\d\d\.(\d\d\d\d|\d\d)')

# for group in GROUP_NAMES:
#     date = date_reg.search(group)
#     day, month, year = date.group().split('.')
#     year = f'20{year}' if len(year) == 2 else year
#     date = f'{day}.{month}.{year}'
#     print(date)

import pymongo
import pprint

# Create the client
client = pymongo.MongoClient('localhost', 27017)
db = client['poks_bot_db']
gpa = db['gpa']
emergency_stops = db['emergency_stops']


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


def pop_aos():
    gpa.update_many(
        {},
        {'$set': {'ao': []}}
    )
    qs = list(emergency_stops.find({}))
    count = 0
    for ao in qs:
        gpa_inst = gpa.find_one({'ks': ao.get('station'), 'num_gpa': ao.get('gpa')})
        if gpa_inst is not None:
            ao_list = gpa_inst.get('ao')
            ao_list.append(ao.get('_id'))
            gpa.update_one(
                {'ks': ao.get('station'), 'num_gpa': ao.get('gpa')},
                {'$set': {'ao': ao_list}}
            )
            count += 1
        else:
            continue
    print(count)

pop_aos()
