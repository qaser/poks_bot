from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text

from config.mongo_config import docs


# @dp.callback_query_handler(Text(startswith='docs_'))
async def send_files(call: types.CallbackQuery):
    _, pet_id = call.data.split('_')
    queryset = list(docs.find({'pet_id': pet_id}))
    for file in queryset:
        file_id = file.get('file_id')
        file_type = file.get('file_type')
        if file_type == 'photo':
            await call.message.answer_photo(file_id)
        elif file_type == 'video':
            await call.message.answer_video(file_id)
        elif file_type == 'document':
            await call.message.answer_document(file_id)


def register_callbacks_docs(dp: Dispatcher):
    dp.register_callback_query_handler(
        send_files,
        Text(startswith='docs')
    )
