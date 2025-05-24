

from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
import os
from datetime import datetime,timedelta

class User(db.Model, UserMixin):
    __tablename__ = 'utilisateurs'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)  
    nom = db.Column(db.String(50), nullable=False)    
    role = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                         onupdate=db.func.current_timestamp())
    last_login = db.Column(db.DateTime, nullable=True)  
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    is_confirmed = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def nom_complet(self):
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.prenom} {self.nom}"
    
    @property
    def initiales(self):
        """Retourne les initiales de l'utilisateur"""
        return f"{self.prenom[0]}{self.nom[0]}".upper() if self.prenom and self.nom else "??"

    @property
    def password(self):
        raise AttributeError('Le mot de passe ne peut pas être lu directement')

    @password.setter
    def password(self, password):
        """Setter pour le mot de passe qui génère automatiquement le hash"""
        if len(password) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        self.password_hash = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=16
        )

    def __init__(self, **kwargs):
        """Initialise l'utilisateur avec validation des champs"""
        # Gestion spéciale du mot de passe avant l'initialisation normale
        password = kwargs.pop('password', None)
        super(User, self).__init__(**kwargs)
        
        # Validation des champs requis
        if not self.username or len(self.username.strip()) < 3:
            raise ValueError("Le nom d'utilisateur doit contenir au moins 3 caractères")
            
        if not self.prenom or len(self.prenom.strip()) < 2:
            raise ValueError("Le prénom doit contenir au moins 2 caractères")
            
        if not self.nom or len(self.nom.strip()) < 2:
            raise ValueError("Le nom doit contenir au moins 2 caractères")
        
        # Si un mot de passe est fourni, utilisez le setter
        if password:
            self.password = password
    
    def check_password(self, password):
        """Vérifie si le mot de passe correspond au hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_avatar_path(self):
        """Retourne le chemin relatif de l'avatar"""
        if self.avatar:
            return os.path.join('uploads', self.avatar)
        return 'images/default-avatar.jpg'

    def get_avatar_url(self):
        """Retourne l'URL complète de l'avatar"""
        from flask import url_for
        return url_for('static', filename=self.get_avatar_path())

    def delete_avatar(self):
        """Supprime physiquement le fichier avatar du serveur"""
        if self.avatar:
            try:
                upload_folder = current_app.config['UPLOAD_FOLDER']
                avatar_path = os.path.join(upload_folder, self.avatar)
                if os.path.exists(avatar_path):
                    os.remove(avatar_path)
            except Exception as e:
                current_app.logger.error(f"Erreur suppression avatar: {str(e)}")

    def before_delete(self):
        """Nettoyage avant suppression de l'utilisateur"""
        self.delete_avatar()

    def update_last_seen(self):
        """Met à jour le timestamp de dernière activité"""
        self.updated_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username} ({self.email})>'

    def to_dict(self):
        """Retourne une représentation dictionnaire de l'utilisateur"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'prenom': self.prenom,
            'nom': self.nom,
            'role': self.role,
            'avatar_url': self.get_avatar_url(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    def update_login_time(self):
        self.last_login = datetime.now()
        db.session.commit()

    def get_presence_status(self):
        # Implémenter ma logique de présence ici
        # Par exemple, vérifier last_activity dans la base de données
        if self.last_activity > datetime.utcnow() - timedelta(minutes=5):
            return 'online'
        elif self.last_activity > datetime.utcnow() - timedelta(minutes=30):
            return 'away'
        else:
            return 'offline'