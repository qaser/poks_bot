from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scheduler.scheduler_funcs import (send_mail_summary, send_remainder,
                                       send_task_users_reminder, send_backups)
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
    scheduler.add_job(
        send_mail_summary,
        'cron',
        day_of_week='mon',
        hour=8,
        minute=30,
        timezone=TIME_ZONE,
        args=['week']
    )
    scheduler.add_job(
        send_mail_summary,
        'cron',
        day=1,
        hour=8,
        minute=31,
        timezone=TIME_ZONE,
        args=['month']
    )
    scheduler.add_job(
        send_task_users_reminder,
        'cron',
        day_of_week='wed',
        hour=10,
        minute=15,
        timezone=TIME_ZONE
    )
    scheduler.add_job(
        send_backups,
        'cron',
        day_of_week='mon-sun',
        hour=14,
        minute=10,
        timezone=TIME_ZONE
    )
    # scheduler.add_job(
    #     check_mailbox,
    #     'interval',
    #     minutes=1,
    #     timezone=TIME_ZONE
    # )
