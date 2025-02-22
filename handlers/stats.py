from aiogram import Dispatcher, types

import keyboards.for_stats as kb
from config.bot_config import dp
from config.mongo_config import emergency_stops
from utils.decorators import admin_check


@admin_check
@dp.message_handler(commands=['stats'])
async def stats_handler(message: types.Message):
    if message.chat.type == 'private':
        res_text = ''
        count_ao = emergency_stops.count_documents({})
        pipeline = [
            {'$group': {'_id': '$station', 'count': {'$sum': 1}}},
            {'$sort': { 'count': -1}}
        ]
        queryset = list(emergency_stops.aggregate(pipeline))
        for item in queryset:
            name = item.get('_id')
            count = item.get('count')
            station_text = f'{name}: {count}\n'
            res_text = f'{res_text}{station_text}'
        summary_text = f'Всего ботом учтено АО(ВНО): {count_ao}\n\n{res_text}'
        await message.delete()
        await message.answer(
            summary_text,
            reply_markup=kb.sort_kb('ks')
        )


def register_handlers_stats(dp: Dispatcher):
    dp.register_message_handler(stats_handler, commands='stats')
