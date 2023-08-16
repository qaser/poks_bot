import datetime as dt

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import CantInitiateConversation
from bson.objectid import ObjectId

import keyboards.for_petition as kb
import utils.constants as const
from config.bot_config import bot, dp
from config.mongo_config import admins, buffer, petitions, users


def get_creator(user_id):
    if user_id is not None:
        creator_admin = admins.find_one({'user_id': user_id})
        creator_user = users.find_one({'user_id': user_id})
        if creator_admin is None and creator_user is None:
            creator_name = 'Неизвестен'
        elif creator_admin is not None:
            creator_name = creator_admin.get('username')
        elif creator_user is not None:
            creator_name = creator_user.get('username')
        return creator_name
    else:
        return 'Неизвестен'
