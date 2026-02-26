from app import db
import sqlalchemy.orm as so
import sqlalchemy as sa
from datetime import datetime, timezone

class Notification(db.Model):
    notification_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    message: so.Mapped[str] = so.mapped_column(sa.String(256),nullable=False)
    created_at: so.Mapped[datetime] = so.mapped_column(
    sa.DateTime, default=lambda: datetime.now(timezone.utc))
    type: so.Mapped[str] = so.mapped_column(sa.String(256))
    link: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=True)
    read: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False, default=False)

class User(db.Model):
    user_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    course: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    year_of_study: so.Mapped[int] = so.mapped_column(sa.INTEGER, nullable=False, default=0)
    password: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)

    __table_args__ = (db.UniqueConstraint("email"),)

class Resource(db.Model):
    resource_id: so.Mapped[int] = so.mapped_column(primary_key=True)
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

    date: so.Mapped[datetime] = so.mapped_column(sa.Date, nullable=False)

    def overall_rating(self):
        return round((self.stress + self.sleep + self.social + self.academic + self.activity) / 5)

