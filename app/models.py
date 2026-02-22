from app import db
import sqlalchemy.orm as so
import sqlalchemy as sa
from datetime import datetime, timezone

class Notification(db.Model):
    __bind_key__ = 'notifications'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    message: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    noti_date: so.Mapped[datetime] = so.mapped_column(sa.DATE, nullable=False, default=lambda: datetime.now(timezone.utc))
    noti_time: so.Mapped[datetime] = so.mapped_column(sa.TIME, nullable=False, default=lambda: datetime.now(timezone.utc))
    type: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    read: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False, default=False)



