from cgitb import reset
import datetime as dt
import collections, operator
import pprint
import requests

import pymongo
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
# from config.telegram_config import MY_TELEGRAM_ID

client = pymongo.MongoClient('localhost', 27017)
db = client['gks_bot_db']
# fs = gridfs.GridFS(db)
quiz = db['quiz']
users = db['users']
vehicles = db['vehicles']
offers = db['offers']


# date = dt.datetime.today().strftime('%d.%m.%Y')
vehicle_orders = list(vehicles.find({'date': '12.09.2022'}).sort(
    'location',
    pymongo.ASCENDING
))
res = []
for order in vehicle_orders:
    vehicle = order.get('vehicle')
    location = order.get('location')
    time = order.get('time')
    key = f'{location} | {vehicle} | {time}'
    res.append(key)

pprint.pprint(res)
