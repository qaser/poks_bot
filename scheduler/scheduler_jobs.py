from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scheduler.scheduler_funcs import send_remainder

scheduler = AsyncIOScheduler()


def scheduler_jobs():
    # # по будням в 18:00 отправляет заметку о сегодняшнем дне
    # scheduler.add_job(
    #     send_history_day,
    #     'cron',
    #     day_of_week='mon-sun',
    #     hour=18,
    #     minute=0,
    #     timezone=const.TIME_ZONE
    # )
    scheduler.add_job(
        send_remainder,
        'interval',
        seconds=15
    )
