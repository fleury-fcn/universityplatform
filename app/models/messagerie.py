'''from datetime import datetime
from app.extensions import db
import json
import os

message_recipients = db.Table('message_recipients',
    db.Column('message_id', db.Integer, db.ForeignKey('messages.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('utilisateurs.id'), primary_key=True),
    db.Column('is_deleted', db.Boolean, default=False),
    db.Column('read_at', db.DateTime)
)

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted_by_sender = db.Column(db.Boolean, default=False)
    _attachments = db.Column('attachments', db.Text)
    
    # Relations
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_messages', lazy='dynamic'))
    recipients = db.relationship(
        'User',
        secondary=message_recipients,
        backref=db.backref('received_messages', lazy='dynamic'),
        lazy='dynamic'
    )

    @property
    def attachments(self):
        try:
            return json.loads(self._attachments) if self._attachments else []
        except json.JSONDecodeError:
            return []
    
    @attachments.setter
    def attachments(self, value):
        try:
            self._attachments = json.dumps(value) if value else None
        except TypeError:
            self._attachments = None

    def verify_attachments(self):
        """Vérifie que les pièces jointes existent sur le système de fichiers"""
        if not self.attachments:
            return False
            
        for attachment in self.attachments:
            if not os.path.exists(attachment.get('path', '')):
                return False
        return True

    def is_deleted_by(self, user_id):
        """Vérifie si le message a été supprimé par l'utilisateur"""
        if user_id == self.sender_id:
            return self.is_deleted_by_sender
            
        result = db.session.execute(
            db.select(message_recipients.c.is_deleted)
            .where(message_recipients.c.message_id == self.id)
            .where(message_recipients.c.user_id == user_id)
        ).scalar_one_or_none()
        
        return result if result is not None else False

    def mark_as_deleted(self, user_id):
        """Marque le message comme supprimé pour un utilisateur"""
        if user_id == self.sender_id:
            self.is_deleted_by_sender = True
        else:
            db.session.execute(
                message_recipients.update()
                .where(message_recipients.c.message_id == self.id)
                .where(message_recipients.c.user_id == user_id)
                .values(is_deleted=True)
            )
        db.session.commit()

    def mark_as_restored(self, user_id):
        """Restaure le message pour un utilisateur"""
        if user_id == self.sender_id:
            self.is_deleted_by_sender = False
        else:
            db.session.execute(
                message_recipients.update()
                .where(message_recipients.c.message_id == self.id)
                .where(message_recipients.c.user_id == user_id)
                .values(is_deleted=False)
            )
        db.session.commit()
    
    def get_read_status(self, user_id):
        """Retourne la date de lecture pour un utilisateur donné"""
        if user_id == self.sender_id:
            return self.sent_at
            
        result = db.session.execute(
            db.select(message_recipients.c.read_at)
            .where(message_recipients.c.message_id == self.id)
            .where(message_recipients.c.user_id == user_id)
        ).scalar_one_or_none()
        
        return result

    def is_read_by(self, user_id):
        """Vérifie si le message a été lu par un utilisateur spécifique"""
        return self.get_read_status(user_id) is not None

    def __repr__(self):
        return f"<Message {self.id} - {self.subject[:20]}>"
        '''

from datetime import datetime
from app.extensions import db
import json
import os

message_recipients = db.Table('message_recipients',
    db.Column('message_id', db.Integer, db.ForeignKey('messages.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('utilisateurs.id'), primary_key=True),
    db.Column('is_deleted', db.Boolean, default=False),
    db.Column('read_at', db.DateTime)
)

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted_by_sender = db.Column(db.Boolean, default=False)
    _attachments = db.Column('attachments', db.Text)

    # Relations
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_messages', lazy='dynamic'))
    recipients = db.relationship(
        'User',
        secondary=message_recipients,
        backref=db.backref('received_messages', lazy='dynamic'),
        lazy='dynamic'
    )

    @property
    def attachments(self):
        try:
            return json.loads(self._attachments) if self._attachments else []
        except json.JSONDecodeError:
            return []
    
    @attachments.setter
    def attachments(self, value):
        try:
            self._attachments = json.dumps(value) if value else None
        except TypeError:
            self._attachments = None

    def verify_attachments(self):
        """Vérifie que les pièces jointes existent sur le système de fichiers"""
        if not self.attachments:
            return False
            
        for attachment in self.attachments:
            if not os.path.exists(attachment.get('path', '')):
                return False
        return True

    def is_deleted_by(self, user_id):
        """Vérifie si le message a été supprimé par l'utilisateur"""
        if user_id == self.sender_id:
            return self.is_deleted_by_sender
            
        result = db.session.execute(
            db.select(message_recipients.c.is_deleted)
            .where(message_recipients.c.message_id == self.id)
            .where(message_recipients.c.user_id == user_id)
        ).scalar_one_or_none()
        
        return result if result is not None else False

    def mark_as_deleted(self, user_id):
        """Marque le message comme supprimé pour un utilisateur"""
        if user_id == self.sender_id:
            self.is_deleted_by_sender = True
        else:
            db.session.execute(
                message_recipients.update()
                .where(message_recipients.c.message_id == self.id)
                .where(message_recipients.c.user_id == user_id)
                .values(is_deleted=True)
            )
        db.session.commit()

    def mark_as_restored(self, user_id):
        """Restaure le message pour un utilisateur"""
        if user_id == self.sender_id:
            self.is_deleted_by_sender = False
        else:
            db.session.execute(
                message_recipients.update()
                .where(message_recipients.c.message_id == self.id)
                .where(message_recipients.c.user_id == user_id)
                .values(is_deleted=False)
            )
        db.session.commit()
    
    def get_read_status(self, user_id):
        """Retourne la date de lecture pour un utilisateur donné"""
        if user_id == self.sender_id:
            return self.sent_at
            
        result = db.session.execute(
            db.select(message_recipients.c.read_at)
            .where(message_recipients.c.message_id == self.id)
            .where(message_recipients.c.user_id == user_id)
        ).scalar_one_or_none()
        
        return result

    def is_read_by(self, user_id):
        """Vérifie si le message a été lu par un utilisateur spécifique"""
        return self.get_read_status(user_id) is not None

    def __repr__(self):
        return f"<Message {self.id} - {self.subject[:20]}>"