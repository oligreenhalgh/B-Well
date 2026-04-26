from app.models import *
from datetime import datetime

def setup():
    db.drop_all()
    db.create_all()

    #Users

    student = User(id = 1, username='test', email='test@student.bham.ac.uk')
    student.set_password('Password1')
    db.session.add(student)

    student2 = User(id = 2, username='test2', email='test2@student.bham.ac.uk')
    student2.set_password('Password1')
    db.session.add(student2)

    student3 = User(id = 3, username='test3', email='test3@student.bham.ac.uk')
    student3.set_password('Password1')
    db.session.add(student3)

    admin = User(id = 4, username='admin', email='admin@bham.ac.uk', is_admin=True)
    admin.set_password('Password1')
    db.session.add(admin)

    #Resources

    sleep_r = Resource(resource_id = 1, title = "How to Fall Asleep Faster and Sleep Better", category = "sleep", url = "https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/how-to-fall-asleep-faster-and-sleep-better/")
    db.session.add(sleep_r)

    stress_r = Resource(resource_id = 2, title = "Managing Stress and Building Resilience", category = "stress", url = "https://www.mind.org.uk/information-support/types-of-mental-health-problems/stress/managing-stress-and-building-resilience/")
    db.session.add(stress_r)

    social_r = Resource(resource_id = 3, title = "Time Management Strategies", category = "social", url = "https://www.calendar.com/blog/7-time-management-strategies-for-building-an-eventful-social-life/")
    db.session.add(social_r)

    activity_r = Resource(resource_id = 4, title = "How to Fit Exercise in to Your Working Day", category = "activity", url = "https://www.harpersbazaar.com/uk/wellness/a38678/how-to-fit-exercise-into-your-working-day/")
    db.session.add(activity_r)

    academic_r = Resource(resource_id = 5, title = "Memory Techniques for Revision", category = "academic", url = "https://libguides.bham.ac.uk/asc/memorytechniques")
    db.session.add(academic_r)

    #Notifications

    not_1 = Notification(notification_id = 1, created_at = datetime(2026, 4, 19, 14, 30, 0), read = True, student_id = 1)
    db.session.add(not_1)

    not_2 = Notification(notification_id = 2, created_at = datetime(2026, 4, 20, 14, 30, 0), read = True, student_id = 1)
    db.session.add(not_2)

    not_3 = Notification(notification_id = 3, created_at = datetime(2026, 4, 21, 14, 30, 0), read = True, student_id = 1)
    db.session.add(not_3)

    not_4 = Notification(notification_id = 4, created_at = datetime(2026, 4, 22, 14, 30, 0), read = True, student_id = 1)
    db.session.add(not_4)

    not_5 = Notification(notification_id = 5, created_at = datetime(2026, 4, 23, 14, 30, 0), read = True, student_id = 1)
    db.session.add(not_5)

    not_6 = Notification(notification_id = 6, created_at = datetime(2026, 4, 24, 14, 30, 0), read = True, student_id = 1)
    db.session.add(not_6)

    not_7 = Notification(notification_id=7, created_at=datetime(2026, 4, 25, 14, 30, 0), read=True, student_id=1)
    db.session.add(not_7)

    #Wellbeing Forms

    form_1 = WellbeingResponse(wellbeing_response_id=1, notification_id=1, student_id=1,date=datetime(2026, 4, 19, 14, 40, 0),stress=2,sleep=4,social=3,academic=3,activity=3)
    db.session.add(form_1)

    form_2 = WellbeingResponse(wellbeing_response_id=2, notification_id=2, student_id=1,date=datetime(2026, 4, 20, 14, 40, 0),stress=2,sleep=4,social=5,academic=1,activity=3)
    db.session.add(form_2)

    form_3 = WellbeingResponse(wellbeing_response_id=3, notification_id=3, student_id=1,date=datetime(2026, 4, 21, 14, 40, 0),stress=2,sleep=4,social=3,academic=3,activity=4)
    db.session.add(form_3)

    form_4 = WellbeingResponse(wellbeing_response_id=4, notification_id=4, student_id=1,date=datetime(2026, 4, 22, 14, 40, 0),stress=3,sleep=3,social=4,academic=2,activity=4)
    db.session.add(form_4)

    form_5 = WellbeingResponse(wellbeing_response_id=5, notification_id=5, student_id=1,date=datetime(2026, 4, 23, 14, 40, 0),stress=2,sleep=4,social=2,academic=3,activity=2)
    db.session.add(form_5)

    form_6 = WellbeingResponse(wellbeing_response_id=6, notification_id=6, student_id=1,date=datetime(2026, 4, 24, 14, 40, 0),stress=4,sleep=2,social=2,academic=4,activity=3)
    db.session.add(form_6)

    form_7 = WellbeingResponse(wellbeing_response_id=7, notification_id=7, student_id=1, date=datetime(2026, 4, 25, 14, 40, 0), stress=4, sleep=3, social=2, academic=5, activity=3)
    db.session.add(form_7)

    db.session.commit()