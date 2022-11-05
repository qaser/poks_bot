import os

import gridfs
import pymongo

client = pymongo.MongoClient('localhost', 27017)
# Connect to our database
db = client['gks_bot_db']
key_rules = db['key_rules']
fs = gridfs.GridFS(db)

for root, dirs, files in os.walk('static/kpb_lite/'):
    for filename in files:
        file = f'static/kpb_lite/{filename}'
        with open(file, 'rb') as f:
            contents = f.read()
        fs.put(contents, unit='kpb')

for root, dirs, files in os.walk('static/ns/'):
    for filename in files:
        file = f'static/ns/{filename}'
        with open(file, 'rb') as f:
            contents = f.read()
        fs.put(contents, unit='ns')
