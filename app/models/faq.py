"""Questions fréquentes sur la vie à l'ISTA et l'utilisation de l'application."""
from app.extensions import db

from . import TimestampMixin


class FaqEntry(TimestampMixin, db.Model):
    __tablename__ = "faq_entries"

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(60), nullable=False, default="Application")
    keywords = db.Column(db.String(255))
    position = db.Column(db.Integer, nullable=False, default=0)
    is_demo = db.Column(db.Boolean, nullable=False, default=False)
