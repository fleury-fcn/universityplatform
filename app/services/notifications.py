"""Envoi de notifications à un ensemble d'utilisateurs."""
from sqlalchemy import insert, update

from app.core.security import ROLE_STUDENT
from app.extensions import db
from app.models import Notification, User, utcnow


def recipients(promotion_id=None, include_staff=True):
    """Identifiants des comptes actifs concernés : tout l'institut, ou une promotion."""
    query = db.session.query(User.id).filter(User.is_active.is_(True))
    if promotion_id:
        condition = User.promotion_id == promotion_id
        if include_staff:
            condition = db.or_(condition, User.role != ROLE_STUDENT)
        query = query.filter(condition)
    return [row.id for row in query]


def notify(user_ids, kind, title, url=None, exclude=None):
    rows = [
        {"user_id": uid, "kind": kind, "title": title[:200], "url": url, "created_at": utcnow()}
        for uid in set(user_ids)
        if uid != exclude
    ]
    if rows:
        db.session.execute(insert(Notification), rows)
        from .push import queue_push

        queue_push([row["user_id"] for row in rows], title, url)
    return len(rows)


def mark_read(user_id, url=None):
    stmt = update(Notification).where(Notification.user_id == user_id, Notification.read_at.is_(None))
    if url:
        stmt = stmt.where(Notification.url == url)
    db.session.execute(stmt.values(read_at=utcnow()))
