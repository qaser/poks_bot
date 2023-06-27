from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scheduler.scheduler_funcs import send_remainder, check_mailbox
from utils.constants import TIME_ZONE

scheduler = AsyncIOScheduler()


def scheduler_jobs():
    # по будням в 18:00 отправляет напоминание о предоставлении отчёта
    scheduler.add_job(
        send_remainder,
        'cron',
        day_of_week='mon-sun',
        hour=18,
        minute=0,
        timezone=TIME_ZONE
    )
    # scheduler.add_job(
    #     check_mailbox,
    #     'interval',
    #     minutes=1,
    #     timezone=TIME_ZONE
    # )
