"""Tuyaux : bons plans et conseils entre étudiants, modérés."""
from app.extensions import db

from . import TimestampMixin

PENDING, PUBLISHED, REJECTED = "en_attente", "publie", "refuse"


class Tip(TimestampMixin, db.Model):
    __tablename__ = "tips"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), nullable=False, default="autre")
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id", ondelete="SET NULL"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    file_id = db.Column(db.Integer, db.ForeignKey("stored_files.id"))
    status = db.Column(db.String(12), nullable=False, default=PENDING, index=True)
    moderation_note = db.Column(db.String(300))
    moderated_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    published_at = db.Column(db.DateTime, index=True)
    is_demo = db.Column(db.Boolean, nullable=False, default=False)

    author = db.relationship("User", foreign_keys=[author_id])
    course = db.relationship("Course")
    file = db.relationship("StoredFile")
    votes = db.relationship("TipVote", cascade="all, delete-orphan")
    reports = db.relationship("TipReport", cascade="all, delete-orphan")

    def visible_to(self, user):
        return self.status == PUBLISHED or user.is_admin or self.author_id == user.id


class TipVote(db.Model):
    __tablename__ = "tip_votes"

    tip_id = db.Column(db.Integer, db.ForeignKey("tips.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)


class TipReport(TimestampMixin, db.Model):
    __tablename__ = "tip_reports"
    __table_args__ = (db.UniqueConstraint("tip_id", "user_id", name="uq_tip_report"),)

    id = db.Column(db.Integer, primary_key=True)
    tip_id = db.Column(db.Integer, db.ForeignKey("tips.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reason = db.Column(db.String(300), nullable=False)

    user = db.relationship("User")
