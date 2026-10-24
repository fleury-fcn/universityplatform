"""Lieux du campus : salles, amphithéâtres, services."""
from app.extensions import db

from . import TimestampMixin

ROOM_KINDS = ("amphi", "salle", "labo", "bibliotheque", "bureau", "service", "autre")


class Room(TimestampMixin, db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    kind = db.Column(db.String(20), nullable=False, default="salle")
    building = db.Column(db.String(120))
    floor = db.Column(db.String(30))
    capacity = db.Column(db.Integer)
    description = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_demo = db.Column(db.Boolean, nullable=False, default=False)

    def __str__(self):
        return self.name
