from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified

import keyboards.for_stats as kb
from config.mongo_config import emergency_stops, gpa


async def sort_stats(call: types.CallbackQuery):
    _, sort_param = call.data.split('_')
    if sort_param == 'gpa':
        pipeline = [
            {'$match': {'ao': {'$exists': 'true'}}},
            {'$project': {
                'name_gpa': 1,
                'numberOfAO': {
                    '$cond': {
                        'if': {'$isArray': "$ao"},
                        'then': { '$size': "$ao" },
                        'else': "NA"
                    }
                }
            }
            },
            {'$group': {'_id': '$name_gpa', 'count': {'$sum': '$numberOfAO'}}},
            {'$sort': { 'count': -1}}
        ]
        queryset = list(gpa.aggregate(pipeline))
    else:
        pipeline = [
            {'$group': {'_id': '$station', 'count': {'$sum': 1}}},
            {'$sort': { 'count': -1}}
        ]
        queryset = list(emergency_stops.aggregate(pipeline))
    res_text = ''
    count_ao = emergency_stops.count_documents({})
    for item in queryset:
        name = item.get('_id')
        count = item.get('count')
        stats_text = f'{name}: <b>{count}</b>\n'
        res_text = f'{res_text}{stats_text}'
    summary_text = f'Всего ботом учтено АО(ВНО): {count_ao}\n\n{res_text}'
    try:
        await call.message.edit_text(
            summary_text,
            reply_markup=kb.sort_kb(sort_param),
            parse_mode=types.ParseMode.HTML
        )
    except MessageNotModified:
        summary_text = f'Ботом учтено АО(ВНО): {count_ao}\n\n{res_text}'
        await call.message.edit_text(
            summary_text,
            reply_markup=kb.sort_kb(sort_param),
            parse_mode=types.ParseMode.HTML
        )



def register_callbacks_sort(dp: Dispatcher):
    dp.register_callback_query_handler(
        sort_stats,
        Text(startswith='sort'),
    )
