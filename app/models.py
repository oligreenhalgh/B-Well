from click.types import UUIDParameterType

from app import db
import sqlalchemy.orm as so
import sqlalchemy as sa
from datetime import datetime, timezone

class Notification(db.Model):
    __bind_key__ = 'notifications'
    notification_id: so.Mapped[UUIDParameterType] = so.mapped_column(primary_key=True)
    message: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    noti_date: so.Mapped[datetime] = so.mapped_column(sa.DATE, nullable=False, default=lambda: datetime.now(timezone.utc))
    noti_time: so.Mapped[datetime] = so.mapped_column(sa.TIME, nullable=False, default=lambda: datetime.now(timezone.utc))
    type: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    read: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False, default=False)

class User(db.Model):
    __bind_key__ = 'users'
    user_id: so.Mapped[UUIDParameterType] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    course: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    year_of_study: so.Mapped[int] = so.mapped_column(sa.INTEGER, nullable=False, default=0)

class CheckIn(db.Model):
    __bind_key__ = 'checkins'
    checkin_id: so.Mapped[UUIDParameterType] = so.mapped_column(primary_key=True)
    stress_rating: so.Mapped[int] = so.mapped_column(sa.INTEGER, nullable=False, default=0)
    social_rating: so.Mapped[int] = so.mapped_column(sa.INTEGER, nullable=False, default=0)
    academic_rating: so.Mapped[int] = so.mapped_column(sa.INTEGER, nullable=False, default=0)
    physical_health_rating: so.Mapped[int] = so.mapped_column(sa.INTEGER, nullable=False, default=0)
    overall_rating: so.Mapped[int] = so.mapped_column(sa.INTEGER, nullable=False, default=0)
    notes: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)


class Resource(db.Model):
    __bind_key__ = 'resources'
    resource_id: so.Mapped[UUIDParameterType] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(256))
    category: so.Mapped[str] = so.mapped_column(sa.String(256))
    description: so.Mapped[str] = so.mapped_column(sa.String(256))
    url: so.Mapped[str] = so.mapped_column(sa.String(256))

class Wellbeing(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    stress: so.Mapped[int] = so.mapped_column(nullable=False)
    sleep: so.Mapped[int] = so.mapped_column(nullable=False)
    social: so.Mapped[int] = so.mapped_column(nullable=False)
    academic: so.Mapped[int] = so.mapped_column(nullable=False)
    activity: so.Mapped[int] = so.mapped_column(nullable=False)

    notes: so.Mapped[str] = so.mapped_column(sa.String(500), nullable=True)

    submitted_on: so.Mapped[datetime] = so.mapped_column(
        sa.Date,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).date()
    )

    def overall_rating(self):
        return round(
            (self.stress + self.sleep + self.social + self.academic + self.activity) / 5
        )

