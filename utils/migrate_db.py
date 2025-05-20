import datetime as dt

import pymongo

# # Create the client
client = pymongo.MongoClient('localhost', 27017)
db = client['poks_bot_db']
gpa = db['gpa']


gpa_filter_1 = {'ks': 'Ямбургская КС', 'num_shop': 'СОГ-1',}
gpa_filter_2 = {'ks': 'Ямбургская КС', 'num_shop': 'СОГ-3',}

gpa.update_many(
    gpa_filter_2,
    {'$set': {'type_gpa': 'Судовой привод'}}
)

gpa.update_many(
    gpa_filter_1,
    {'$set': {'type_gpa': 'Судовой привод'}}
)
