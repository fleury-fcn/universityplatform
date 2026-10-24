"""Bibliothèque : catalogue et réservations."""
from app.extensions import db

from . import TimestampMixin, utcnow

BOOK_CATEGORIES = ("statistique", "probabilite", "actuariat", "economie", "data-science", "informatique",
                   "mathematiques", "divers")
# Statuts d'une réservation, dans l'ordre du parcours.
PENDING, READY, BORROWED, RETURNED, CANCELLED, REFUSED = (
    "en_attente", "prete", "empruntee", "rendue", "annulee", "refusee")
ACTIVE_STATUSES = (PENDING, READY, BORROWED)
HOLDING_STATUSES = (READY, BORROWED)  # immobilisent un exemplaire
MAX_ACTIVE_RESERVATIONS = 3


class Book(TimestampMixin, db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(30), nullable=False, default="divers")
    language = db.Column(db.String(5), nullable=False, default="fr")
    isbn = db.Column(db.String(20))
    publisher = db.Column(db.String(120))
    year = db.Column(db.Integer)
    call_number = db.Column(db.String(40))
    copies_total = db.Column(db.Integer, nullable=False, default=1)
    description = db.Column(db.Text)
    file_id = db.Column(db.Integer, db.ForeignKey("stored_files.id"))
    is_demo = db.Column(db.Boolean, nullable=False, default=False)

    file = db.relationship("StoredFile")
    reservations = db.relationship("Reservation", back_populates="book", cascade="all, delete-orphan")

    @property
    def copies_held(self):
        return sum(1 for r in self.reservations if r.status in HOLDING_STATUSES)

    @property
    def copies_available(self):
        return max(self.copies_total - self.copies_held, 0)


class Reservation(TimestampMixin, db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    status = db.Column(db.String(12), nullable=False, default=PENDING, index=True)
    due_date = db.Column(db.Date)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    book = db.relationship("Book", back_populates="reservations")
    user = db.relationship("User")

    @property
    def is_active(self):
        return self.status in ACTIVE_STATUSES
