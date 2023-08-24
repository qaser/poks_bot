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

# Create the client
client = pymongo.MongoClient('localhost', 27017)
db = client['poks_bot_db']
gpa = db['gpa']

def populate_gpa():
    # path = f'C:\Dev\poks_bot\static\\rto'
    path = f'./static/rto'
    f_path = f'{path}/gpa.csv'
    with open(f_path, encoding='utf-8') as file:
        reader = file.readlines()
        for i, row in enumerate(reader):
            if i:
                _, name_gpa, _, shop, _, _, full_num_gpa, cbn_type, _, _, _, _, _, _ = row.split(';')
                gpa.insert_one({
                    'name_gpa': name_gpa,
                    'num_gpa': full_num_gpa,
                    'num_shop': shop,
                    'cbn_type': cbn_type
                })


def pop_name_gpa():
    qs = list(gpa.find({}))
    for i in qs:
        gpa_id = i.get('_id')
        name_gpa = i.get('name_gpa')
        num_shop = i.get('num_shop')
        cbn_type = i.get('cbn_type')

        path_name = f'./static/rto/name_gpa.csv'
        path_group = f'./static/rto/group_name_gpa.csv'
        path_type = f'./static/rto/type_gpa.csv'
        path_between = f'./static/rto/gpaName_engineType.csv'
        path_engine = f'./static/rto/engine_type.csv'
        path_shop = f'./static/rto/shop.csv'
        path_ks = f'./static/rto/ks.csv'
        path_cbn = f'./static/rto/cbn_type.csv'
        path_pipe = f'./static/rto/gas_pipeline.csv'
        path_lpu = f'./static/rto/lpu.csv'

        with open(path_name, encoding='utf-8') as file:
            reader = file.readlines()
            for i, row in enumerate(reader):
                if i:
                    if row.split(';')[0] == name_gpa:
                        n_gpa = row.split(';')[1]
                        group_name = row.split(';')[2].rstrip()
                        with open(path_group, encoding='utf-8') as file:
                            reader = file.readlines()
                            for i, row in enumerate(reader):
                                if i:
                                    if row.split(';')[0] == group_name:
                                        g_name = row.split(';')[1]
                                        id_type = row.split(';')[2]
                                        with open(path_type, encoding='utf-8') as file:
                                            reader = file.readlines()
                                            for i, row in enumerate(reader):
                                                if i:
                                                    if row.split(';')[0] == id_type:
                                                        type_gpa = row.split(';')[1]
        with open(path_between, encoding='utf-8') as file:
            reader = file.readlines()
            for i, row in enumerate(reader):
                if i:
                    if row.split(';')[0] == name_gpa:
                        id_engine_type = row.split(';')[1].rstrip()
                        with open(path_engine, encoding='utf-8') as file:
                            reader = file.readlines()
                            for i, row in enumerate(reader):
                                if i:
                                    if row.split(';')[0] == id_engine_type:
                                        engine_type = row.split(';')[1].rstrip()
        with open(path_shop, encoding='utf-8') as file:
            reader = file.readlines()
            for i, row in enumerate(reader):
                if i:
                    if row.split(';')[0] == num_shop:
                        num_shop = row.split(';')[1]
                        id_ks = row.split(';')[2]
                        id_pipe = row.split(';')[3]
                        with open(path_ks, encoding='utf-8') as file:
                            reader = file.readlines()
                            for i, row in enumerate(reader):
                                if i:
                                    if row.split(';')[0] == id_ks:
                                        try:
                                            KS, name = row.split(';')[1].split(' ')
                                            ks = f'{name} {KS}'
                                        except:
                                            ks = row.split(';')[1]
                                        lpu_id = row.split(';')[2]
                                        with open(path_lpu, encoding='utf-8') as file:
                                            reader = file.readlines()
                                            for i, row in enumerate(reader):
                                                if i:
                                                    if row.split(';')[0] == lpu_id:
                                                        lpu, mg, lpu_name = row.split(';')[1].split(' ')
                                                        lpu = f'{lpu_name} {lpu}{mg}'
                        with open(path_pipe, encoding='utf-8') as file:
                            reader = file.readlines()
                            for i, row in enumerate(reader):
                                if i:
                                    if row.split(';')[0] == id_pipe:
                                        pipeline = row.split(';')[1].rstrip()
        with open(path_cbn, encoding='utf-8') as file:
            reader = file.readlines()
            for i, row in enumerate(reader):
                if i:
                    if row.split(';')[0] == cbn_type:
                        cbn_type = row.split(';')[1].rstrip()
        gpa.update_one(
            {'_id': gpa_id},
            {'$set': {
                'lpu': lpu,
                'ks': ks,
                'pipeline': pipeline,
                'num_shop': num_shop,
                'name_gpa': n_gpa,
                'group_gpa': g_name,
                'type_gpa': type_gpa,
                'cbn_type': cbn_type,
                'engine_type': engine_type,
            }}
        )



populate_gpa()
pop_name_gpa()
