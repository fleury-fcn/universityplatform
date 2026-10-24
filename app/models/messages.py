"""Messagerie interne."""
from app.extensions import db

from . import TimestampMixin

message_attachments = db.Table(
    "message_attachments",
    db.Column("message_id", db.Integer, db.ForeignKey("messages.id", ondelete="CASCADE"), primary_key=True),
    db.Column("file_id", db.Integer, db.ForeignKey("stored_files.id"), primary_key=True),
)


class Message(TimestampMixin, db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    # Renseigné quand le message a été envoyé à toute une promotion.
    promotion_id = db.Column(db.Integer, db.ForeignKey("promotions.id"))
    reply_to_id = db.Column(db.Integer, db.ForeignKey("messages.id"))
    sender_deleted_at = db.Column(db.DateTime)

    sender = db.relationship("User")
    promotion = db.relationship("Promotion")
    recipients = db.relationship("MessageRecipient", back_populates="message", cascade="all, delete-orphan")
    attachments = db.relationship("StoredFile", secondary=message_attachments)

    def recipient_entry(self, user):
        return next((r for r in self.recipients if r.user_id == user.id), None)

    def can_read(self, user):
        if self.sender_id == user.id and self.sender_deleted_at is None:
            return True
        entry = self.recipient_entry(user)
        return entry is not None and entry.deleted_at is None


class MessageRecipient(db.Model):
    __tablename__ = "message_recipients"

    message_id = db.Column(db.Integer, db.ForeignKey("messages.id", ondelete="CASCADE"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True, index=True)
    read_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    message = db.relationship("Message", back_populates="recipients")
    user = db.relationship("User")
