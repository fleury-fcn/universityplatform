"""Modèles de données, un module par domaine fonctionnel."""
from datetime import datetime, timezone

from app.extensions import db


def utcnow():
    """Horodatage UTC sans fuseau (stocké tel quel, converti à l'affichage)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)


from .academic import Department, Program, Promotion  # noqa: E402,F401
from .user import User  # noqa: E402,F401
from .news import News, NewsCategory  # noqa: E402,F401
from .notification import Notification  # noqa: E402,F401
from .campus import Room  # noqa: E402,F401
from .schedule import ScheduleEntry  # noqa: E402,F401
from .files import StoredFile  # noqa: E402,F401
from .courses import Course, Resource  # noqa: E402,F401
