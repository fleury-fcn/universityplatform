

'''from datetime import datetime
from app.extensions import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'  # Nom plus explicite pour la table
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=True)  # Nullable pour les actions système
    action = db.Column(db.String(500), nullable=False)
    details = db.Column(db.Text)  # Pour stocker des détails supplémentaires en JSON
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # Index pour les recherches par date
    ip_address = db.Column(db.String(50))
    entity_type = db.Column(db.String(50))  # Type d'entité concernée (user, course, tuyau, etc.)
    entity_id = db.Column(db.Integer)  # ID de l'entité concernée
    
    
    # Relation avec l'utilisateur
    user = db.relationship('User', backref=db.backref('activity_logs', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ActivityLog {self.id} - {self.action}>'
    
    @classmethod
    def create_log(cls, user_id, action, ip_address=None, entity_type=None, entity_id=None, details=None):
        """Méthode utilitaire pour créer un nouveau log d'activité"""
        log = cls(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details
        )
        db.session.add(log)
        return log
    
    def to_dict(self):
        """Convertit le log en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.nom_complet if self.user else 'Système',
            'action': self.action,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details
        }
    
    @classmethod
    def get_recent_activities(cls, limit=50):
        """Récupère les activités récentes"""
        return cls.query.order_by(cls.timestamp.desc()).limit(limit).all()
    
    # Exemple de modèle Notification
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    subject = db.Column(db.String(255))
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)'''

from datetime import datetime
from app.extensions import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'  # Nom plus explicite pour la table
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=True)  # Nullable pour les actions système
    action = db.Column(db.String(500), nullable=False)
    details = db.Column(db.Text)  # Pour stocker des détails supplémentaires en JSON
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # Index pour les recherches par date
    ip_address = db.Column(db.String(50))
    entity_type = db.Column(db.String(50))  # Type d'entité concernée (user, course, tuyau, etc.)
    entity_id = db.Column(db.Integer)  # ID de l'entité concernée
    
    # Relation avec l'utilisateur
    user = db.relationship('User', backref=db.backref('activity_logs', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ActivityLog {self.id} - {self.action}>'
    
    @classmethod
    def create_log(cls, user_id, action, ip_address=None, entity_type=None, entity_id=None, details=None):
        """Méthode utilitaire pour créer un nouveau log d'activité"""
        log = cls(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details
        )
        db.session.add(log)
        return log
    
    def to_dict(self):
        """Convertit le log en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.nom_complet if self.user else 'Système',
            'action': self.action,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details
        }
    
    @classmethod
    def get_recent_activities(cls, limit=50):
        """Récupère les activités récentes"""
        return cls.query.order_by(cls.timestamp.desc()).limit(limit).all()

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    subject = db.Column(db.String(255))
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation avec l'utilisateur
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Notification {self.subject} - {self.date_sent}>'