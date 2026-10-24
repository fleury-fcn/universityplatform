"""Fichiers déposés par les utilisateurs (stockés hors du dossier static)."""
from app.extensions import db

from . import TimestampMixin


class StoredFile(TimestampMixin, db.Model):
    __tablename__ = "stored_files"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20), nullable=False, index=True)
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(64), unique=True, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    owner = db.relationship("User")

    @property
    def extension(self):
        return self.original_name.rsplit(".", 1)[-1].lower() if "." in self.original_name else ""
