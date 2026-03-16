from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
import sqlalchemy.orm as so
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False, unique=True)
    course: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False)
    year_of_study: so.Mapped[int] = so.mapped_column(sa.INTEGER, nullable=False)
    password_hash: so.Mapped[str] = so.mapped_column(db.String, nullable=False)

    responses: Mapped[list['WellbeingResponse']] = relationship(back_populates="student", cascade="all, delete-orphan")
    notifications: Mapped[list['Notification']] = relationship(back_populates="student", cascade="all, delete-orphan", uselist=False)

    def __repr__(self) -> str:
        return f'<user {self.username}>'

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

class Notification(db.Model):
    __tablename__ = 'notification'
    notification_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    message: so.Mapped[str] = so.mapped_column(sa.String(256),nullable=False)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    type: so.Mapped[str] = so.mapped_column(sa.String(256))
    link: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=True)
    read: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False, default=False)
    student_id: Mapped[int] = mapped_column(sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True, )

    response: Mapped['WellbeingResponse'] = relationship(back_populates="notification", cascade="all, delete-orphan")

    student: Mapped[User] = relationship(back_populates="notifications", foreign_keys=[student_id], )

class Resource(db.Model):
    __tablename__ = 'resource'
    resource_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(256))
    category: so.Mapped[str] = so.mapped_column(sa.String(256))
    url: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False)

class WellbeingResponse(db.Model):
    __tablename__ = 'wellbeing_response'
    wellbeing_response_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    notification_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("notification.notification_id", ondelete="CASCADE"), unique=True, nullable=False)
    student_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    date: so.Mapped[datetime] = so.mapped_column(sa.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    stress: so.Mapped[int] = so.mapped_column(nullable=False)
    sleep: so.Mapped[int] = so.mapped_column(nullable=False)
    social: so.Mapped[int] = so.mapped_column(nullable=False)
    academic: so.Mapped[int] = so.mapped_column(nullable=False)
    activity: so.Mapped[int] = so.mapped_column(nullable=False)
    notes: so.Mapped[str] = so.mapped_column(sa.String(500), nullable=True)

    student: Mapped[User] = relationship(back_populates="responses", foreign_keys=[student_id], )
    notification: Mapped[Notification] = relationship(back_populates="response", foreign_keys=[notification_id], )

    def overall_rating(self):
        return round((self.stress + self.sleep + self.social + self.academic + self.activity) / 5)

@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))