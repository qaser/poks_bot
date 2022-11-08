from apscheduler.schedulers.asyncio import AsyncIOScheduler


scheduler = AsyncIOScheduler()


def scheduler_jobs():
    pass
    # # по будням в 15:00 отправляет заметку о сегодняшнем дне
    # scheduler.add_job(
    #     send_history_day,
    #     'cron',
    #     day_of_week='mon-sun',
    #     hour=15,
    #     minute=0,
    #     timezone=const.TIME_ZONE
    # )
    # # по будням в 07:05 отправляет утреннее приветствие
    # scheduler.add_job(
    #     send_morning_hello,
    #     'cron',
    #     day_of_week='mon-sun',
    #     hour=7,
    #     minute=00,
    #     timezone=const.TIME_ZONE
    # )
    # scheduler.add_job(
    #     send_evening_hello,
    #     'cron',
    #     day_of_week='mon-sun',
    #     hour=19,
    #     minute=00,
    #     timezone=const.TIME_ZONE
    # )
    # scheduler.add_job(
    #     send_morning_wish,
    #     'cron',
    #     day_of_week='mon-sun',
    #     hour=8,
    #     minute=0,
    #     timezone=const.TIME_ZONE
    # )
    # scheduler.add_job(
    #     send_quiz_shedule,
    #     'cron',
    #     day_of_week='mon-sun',
    #     hour=10,
    #     minute=0,
    #     timezone=const.TIME_ZONE
    # )
    # # по будням проверяет дату и отправляет напоминание о 2-ом уровне АПК
    # scheduler.add_job(
    #     send_apk_2_remainder,
    #     'cron',
    #     day_of_week='mon-fri',
    #     hour=10,
    #     minute=15,
    #     timezone=const.TIME_ZONE
    # )
    # scheduler.add_job(
    #     send_tu_theme,
    #     'cron',
    #     day_of_week='mon-sun',
    #     hour=8,
    #     minute=0,
    #     timezone=const.TIME_ZONE
    # )
