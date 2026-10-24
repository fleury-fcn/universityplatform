"""Notifications dans l'application."""
from app.extensions import db

from . import TimestampMixin


class Notification(TimestampMixin, db.Model):
    __tablename__ = "notifications"
    __table_args__ = (db.Index("ix_notifications_user_unread", "user_id", "read_at"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    kind = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(300))
    read_at = db.Column(db.DateTime)


class PushSubscription(TimestampMixin, db.Model):
    """Abonnement aux notifications push d'un navigateur (facultatif, voir VAPID_* dans .env)."""

    __tablename__ = "push_subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint = db.Column(db.String(500), unique=True, nullable=False)
    p256dh = db.Column(db.String(200), nullable=False)
    auth = db.Column(db.String(100), nullable=False)
