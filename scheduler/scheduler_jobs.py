from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scheduler.scheduler_funcs import send_remainder
from utils.constants import TIME_ZONE

scheduler = AsyncIOScheduler()


def scheduler_jobs():
    # по будням в 18:00 отправляет заметку о сегодняшнем дне
    scheduler.add_job(
        send_remainder,
        'cron',
        day_of_week='mon-sun',
        hour=9,
        minute=25,
        timezone=TIME_ZONE
    )
    # scheduler.add_job(
    #     send_remainder,
    #     'interval',
    #     seconds=15,
    #     timezone=TIME_ZONE
    # )
