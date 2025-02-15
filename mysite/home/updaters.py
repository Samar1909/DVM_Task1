from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

def start():
    from home.models import update_schedule
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_schedule, 'interval', days = 7, next_run_time=datetime.now())
    scheduler.start()
    print("Scheduler started")
