from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app import db
from app.models import Notification

scheduler = BackgroundScheduler()

def create_daily_notification():
    from app import app
    with app.app_context():
        notification = Notification(
            message="Please complete your daily wellbeing check-in.",
            type="daily",
            link="/wellbeing"
        )
        db.session.add(notification)
        db.session.commit()
        print("Daily notification created.")

def start_scheduler(app):
    scheduler.start()

    # FOR DEMO: run every minute
    scheduler.add_job(
        func=create_daily_notification,
        trigger="interval",
        minutes=1
    )