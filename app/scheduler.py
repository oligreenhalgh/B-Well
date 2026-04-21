from apscheduler.schedulers.background import BackgroundScheduler
from app import db
from app.models import Notification, User

scheduler = BackgroundScheduler()

def create_daily_notification():
    from app import app
    from datetime import datetime, timezone
    import sqlalchemy as sa

    with app.app_context():
        users = User.query.filter_by(is_admin=False).all()
        today = datetime.now(timezone.utc).date()
        created_count = 0

# checks for users, if no notification exists on this day for this user, create one
        for user in users:
            existing = db.session.query(Notification).filter(
                Notification.student_id == user.id,
                Notification.type == "daily",
                sa.func.date(Notification.created_at) == today
            ).first()

            if not existing:
                notification = Notification(
                    message="Please complete your daily wellbeing check-in.",
                    type="daily",
                    link="/wellbeing",
                    student_id=user.id
                )
                db.session.add(notification)
                db.session.commit()
                created_count += 1

        if created_count > 0:
            print(f"{created_count} daily notification(s) created.")
        else:
            print("No new notifications created.")


def start_scheduler(app):
    scheduler.start()

    # FOR DEMO: run every minute
    scheduler.add_job(
        func=create_daily_notification,
        trigger="interval",
        minutes=1,
        id = "demo_job"
    )

#LOGIC BELOW CAN BE USED TO GENERATE NOTIFICATIONS AT A RANDOM TIME 'BEREAL STYLE'
#For the purposes of demonstration, this should be disabled

# import random
#
# def schedule_random_daily():
#     hour = random.randint(9, 21)
#     minute = random.randint(0, 59)
#
#     scheduler.add_job(
#         func=create_daily_notification,
#         trigger="cron",
#         hour=hour,
#         minute=minute,
#         id="daily_random",
#         replace_existing=True
#     )