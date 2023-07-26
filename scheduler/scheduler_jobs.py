from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scheduler.scheduler_funcs import send_remainder
from utils.create_summary_docx import create_docx_file
from utils.send_email import send_email
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
        create_docx_file,
        'cron',
        day_of_week='thu',
        hour=8,
        minute=55,
        timezone=TIME_ZONE
    )
    scheduler.add_job(
        send_email,
        'cron',
        day_of_week='thu',
        hour=9,
        minute=0,
        timezone=TIME_ZONE
    )
    # scheduler.add_job(
    #     check_mailbox,
    #     'interval',
    #     minutes=1,
    #     timezone=TIME_ZONE
    # )
