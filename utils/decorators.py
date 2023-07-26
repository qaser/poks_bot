import functools
import inspect

from config.bot_config import bot
from config.mongo_config import admins
from config.telegram_config import MY_TELEGRAM_ID


def admin_check(f):
    '''Проверка пользователя на права администратора'''
    @functools.wraps(f)
    async def wrapped_func(*args, **kwargs):
        func_args = inspect.getcallargs(f, *args, **kwargs)
        post = func_args['message']
        if admins.find_one({'user_id': post.from_user.id}) is None:
            await bot.delete_message(
                chat_id=post.from_user.id,
                message_id=post.message_id
            )
            try:
                await bot.send_message(
                    post.from_user.id,
                    'Вам не доступна эта команда'
                )
            except:
                pass
        else:
            return await f(*args, **kwargs)
    return wrapped_func


def superuser_check(f):
    '''Проверка на мой id'''
    @functools.wraps(f)
    async def wrapped_func(*args, **kwargs):
        func_args = inspect.getcallargs(f, *args, **kwargs)
        user_id = func_args['message'].from_user.id
        if user_id != int(MY_TELEGRAM_ID):
            await bot.send_message(user_id, 'Вам не доступна эта команда')
        else:
            return await f(*args, **kwargs)
    return wrapped_func


def run_before(lastfunc, *args1, **kwargs1):
    def run(func):
        def wrapped_func(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except:
                result = None
            finally:
                lastfunc(*args1, **kwargs1)
                return result
        return wrapped_func
    return run
