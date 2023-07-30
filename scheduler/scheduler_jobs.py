from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scheduler.scheduler_funcs import send_remainder, send_task_users_reminder
from utils.constants import TIME_ZONE
from utils.create_summary_docx import create_docx_file
from utils.send_email import send_email

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
        day_of_week='mon',
        hour=8,
        minute=44,
        timezone=TIME_ZONE
    )
    scheduler.add_job(
        send_email,
        'cron',
        day_of_week='mon',
        hour=8,  # изменив здесь время - измени его и в верхней задаче!!!!
        minute=45,
        timezone=TIME_ZONE
    )
    scheduler.add_job(
        send_task_users_reminder,
        'cron',
        day_of_week='wed',
        hour=10,
        minute=15,
        timezone=TIME_ZONE
    )
    # scheduler.add_job(
    #     check_mailbox,
    #     'interval',
    #     minutes=1,
    #     timezone=TIME_ZONE
    # )
