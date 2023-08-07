import datetime as dt
import pymongo


# Create the client
client = pymongo.MongoClient('localhost', 27017)
db = client['poks_bot_db']
petitions = db['petitions']

def status_log():
    queryset = petitions.find({})
    for pet in queryset:
        date = pet.get('date')
        status = pet.get('status')
        status_creator = pet.get('status_creator')
        creator = status_creator if status_creator is not None else pet.get('user_id')
        if status_creator is None:
            petitions.update_one(
                {'_id': pet.get('_id')},
                {'$set': {'status_log': {status: [creator, date]}, 'status_creator': pet.get('user_id')}}
            )
        else:
            petitions.update_one(
                {'_id': pet.get('_id')},
                {'$set': {'status_log': {status: [creator, date]}}}
            )

status_log()
