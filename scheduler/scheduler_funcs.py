from config.bot_config import bot
from config.mongo_config import groups
from texts.initial import REMAINDER


async def send_remainder():
    queryset = list(groups.find({'sub_banned': 'false'}))
    for group in queryset:
        id = group.get('_id')
        try:
            await bot.send_message(
                chat_id=int(id),
                text=REMAINDER
            )
        except:
            pass
