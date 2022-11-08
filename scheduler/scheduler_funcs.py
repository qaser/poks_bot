from config.bot_config import bot
from config.mongo_config import groups


def send_remainder():
    queryset = list(groups.find({'sub_banned': 'false'}))
    for group in queryset:
        id = group.get('_id')
        print(id)
        # await bot.send_message(
        #     chat_id=group.get('_id')
        # )
