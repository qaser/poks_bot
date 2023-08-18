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
petitions = db['petitions']


def add_conversation():
    qs = list(petitions.find({}))
    for pet in qs:
        date = pet.get('date')
        text = pet.get('text')
        user_id = pet.get('user_id')
        petitions.update_one(
            {'_id': pet.get('_id')},
            {'$set': {'conversation': [(date, user_id, text)]}}
        )


add_conversation()
