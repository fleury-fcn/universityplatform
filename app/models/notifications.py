"""
Module de notifications
Système de notifications en temps réel pour alertes académiques
"""
from datetime import datetime
from app.extensions import db
from sqlalchemy import Index


class Notification(db.Model):
    """Notifications pour les utilisateurs"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    
    destinataire_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    
    type_notification = db.Column(db.String(50), nullable=False)  
    # resultat, emploi_temps, absence, message, actualite, evaluation, document
    
    titre = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Données contextuelles
    lien_url = db.Column(db.String(500))  # Lien vers la ressource concernée
    reference_id = db.Column(db.Integer)  # ID de l'objet lié
    reference_type = db.Column(db.String(50))  # Type d'objet (note, seance, etc.)
    
    # Priorité
    priorite = db.Column(db.String(20), default='normale')  # basse, normale, haute, urgente
    
    # Statut
    est_lue = db.Column(db.Boolean, default=False)
    date_lecture = db.Column(db.DateTime)
    
    est_archivee = db.Column(db.Boolean, default=False)
    
    # Dates
    date_creation = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    date_expiration = db.Column(db.DateTime)
    
    # Émetteur
    emetteur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    
    # Relations
    destinataire = db.relationship('User', foreign_keys=[destinataire_id], 
                                   backref=db.backref('notifications_recues', lazy='dynamic'))
    emetteur = db.relationship('User', foreign_keys=[emetteur_id], 
                              backref=db.backref('notifications_envoyees', lazy='dynamic'))
    
    __table_args__ = (
        Index('idx_notif_destinataire', 'destinataire_id'),
        Index('idx_notif_type', 'type_notification'),
        Index('idx_notif_date', 'date_creation'),
        Index('idx_notif_lue', 'est_lue'),
    )
    
    @classmethod
    def creer_notification(cls, destinataire_id, type_notif, titre, message, **kwargs):
        """Méthode helper pour créer une notification"""
        notif = cls(
            destinataire_id=destinataire_id,
            type_notification=type_notif,
            titre=titre,
            message=message,
            **kwargs
        )
        db.session.add(notif)
        db.session.commit()
        return notif
    
    @classmethod
    def notifier_resultats(cls, etudiant_id, evaluation_titre, note):
        """Notifie un étudiant de la publication de ses résultats"""
        return cls.creer_notification(
            destinataire_id=etudiant_id,
            type_notif='resultat',
            titre='Nouveaux résultats disponibles',
            message=f'Vos résultats pour "{evaluation_titre}" sont disponibles. Note: {note}/20',
            priorite='haute'
        )
    
    @classmethod
    def notifier_emploi_temps(cls, destinataires_ids, message_details):
        """Notifie des changements d'emploi du temps"""
        notifications = []
        for dest_id in destinataires_ids:
            notif = cls.creer_notification(
                destinataire_id=dest_id,
                type_notif='emploi_temps',
                titre='Modification emploi du temps',
                message=message_details,
                priorite='haute'
            )
            notifications.append(notif)
        return notifications
    
    @classmethod
    def notifier_absence_enseignant(cls, classe_etudiants_ids, enseignant_nom, date_seance):
        """Notifie les étudiants de l'absence d'un enseignant"""
        notifications = []
        for etudiant_id in classe_etudiants_ids:
            notif = cls.creer_notification(
                destinataire_id=etudiant_id,
                type_notif='absence',
                titre='Absence enseignant',
                message=f'Le cours de {enseignant_nom} prévu le {date_seance} est annulé.',
                priorite='haute'
            )
            notifications.append(notif)
        return notifications
    
    def marquer_comme_lue(self):
        """Marque la notification comme lue"""
        if not self.est_lue:
            self.est_lue = True
            self.date_lecture = datetime.utcnow()
            db.session.commit()
    
    def archiver(self):
        """Archive la notification"""
        self.est_archivee = True
        db.session.commit()
    
    def __repr__(self):
        return f'<Notification {self.type_notification} -> User:{self.destinataire_id}>'


class PreferenceNotification(db.Model):
    """Préférences de notifications par utilisateur"""
    __tablename__ = 'preferences_notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False, unique=True)
    
    # Préférences par type
    notif_resultats = db.Column(db.Boolean, default=True)
    notif_emploi_temps = db.Column(db.Boolean, default=True)
    notif_absences = db.Column(db.Boolean, default=True)
    notif_messages = db.Column(db.Boolean, default=True)
    notif_actualites = db.Column(db.Boolean, default=True)
    notif_evaluations = db.Column(db.Boolean, default=True)
    notif_documents = db.Column(db.Boolean, default=True)
    
    # Canaux de notification
    email_active = db.Column(db.Boolean, default=True)
    push_active = db.Column(db.Boolean, default=True)
    
    # Fréquence
    resume_quotidien = db.Column(db.Boolean, default=False)
    resume_hebdomadaire = db.Column(db.Boolean, default=False)
    
    date_modification = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relations
    user = db.relationship('User', backref=db.backref('preferences_notifications', uselist=False))
    
    def __repr__(self):
        return f'<PreferenceNotification User:{self.user_id}>'
