import datetime as dt
import pymongo


# Create the client
client = pymongo.MongoClient('localhost', 27017)
db = client['poks_bot_db']
petitions = db['petitions']

def format_date():
    queryset = petitions.find({})
    for pet in queryset:
        date = pet.get('date')
        new_date = dt.datetime.strptime(date, '%d.%m.%Y %H:%M')
        print(type(new_date))
        petitions.update_one(
            {'_id': pet.get('_id')},
            {'$set': {'date': new_date}}
        )

format_date()
