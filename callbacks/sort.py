from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text

from config.mongo_config import emergency_stops
import keyboards.for_stats as kb
from aiogram.utils.exceptions import MessageNotModified


async def sort_stats(call: types.CallbackQuery):
    _, sort_param = call.data.split('_')
    if sort_param == 'ks':
        pipeline = [
            {'$group': {'_id': '$station', 'count': {'$sum': 1}}},
            {'$sort': { '_id': 1}}
        ]
    else:
        pipeline = [
            {'$group': {'_id': '$station', 'count': {'$sum': 1}}},
            {'$sort': { 'count': -1}}
        ]
    res_text = ''
    count_ao = emergency_stops.count_documents({})
    queryset = list(emergency_stops.aggregate(pipeline))
    for item in queryset:
        name = item.get('_id')
        count = item.get('count')
        station_text = f'{name}: {count}\n'
        res_text = f'{res_text}{station_text}'
    summary_text = f'Всего ботом учтено АО(ВНО): {count_ao}\n\n{res_text}'
    try:
        await call.message.edit_text(
            summary_text,
            reply_markup=kb.sort_kb(sort_param)
        )
    except MessageNotModified:
        summary_text = f'Ботом учтено АО(ВНО): {count_ao}\n\n{res_text}'
        await call.message.edit_text(
            summary_text,
            reply_markup=kb.sort_kb(sort_param)
        )



def register_callbacks_sort(dp: Dispatcher):
    dp.register_callback_query_handler(
        sort_stats,
        Text(startswith='sort'),
    )
