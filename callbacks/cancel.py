from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters

from config.bot_config import dp


async def ask_cancel(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()


def register_callbacks_cancel(dp: Dispatcher):
    dp.register_callback_query_handler(
        ask_cancel,
        filters.Text(startswith='cancel'),
        state='*'
    )
