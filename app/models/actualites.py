from datetime import datetime
from ..extensions import db
from ..models.Users import User
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



class Actualite(db.Model):
    """
    Modèle pour les actualités de l'ISTA
    """
    __tablename__ = 'actualites'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)  # Pour les URLs SEO
    contenu = db.Column(db.Text, nullable=False)
    resume = db.Column(db.String(300))  # Pour l'aperçu dans la page principale
    categorie = db.Column(db.String(50), nullable=False)  # Événement, Conférence, Diplôme, etc.
    sous_categorie = db.Column(db.String(50))  # Optionnel pour plus de granularité
    image_url = db.Column(db.String(255))  # URL de l'image principale
    image_alt = db.Column(db.String(100))  # Texte alternatif pour l'accessibilité
    date_publication = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_evenement = db.Column(db.DateTime)  # Si c'est un événement futur
    lieu = db.Column(db.String(100))  # Pour les événements
    auteur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    statut = db.Column(db.String(20), default='publie')  # brouillon, publie, archive
    nombre_vues = db.Column(db.Integer, default=0)
    est_important = db.Column(db.Boolean, default=False)  # Pour mise en avant
    mots_cles = db.Column(db.String(255))  # Pour le référencement
    meta_description = db.Column(db.String(160))  # Pour le SEO
    
    # Relations
    auteur = db.relationship('User', backref='actualites')
    commentaires = db.relationship('Commentaire', backref='actualite', lazy='dynamic', cascade='all, delete-orphan')
    pieces_jointes = db.relationship('PieceJointe', backref='actualite', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Actualite {self.titre}>'
    
    def incrementer_vues(self):
        self.nombre_vues += 1
        db.session.commit()
    
    def get_date_formattee(self):
        return self.date_publication.strftime('%d %B %Y à %H:%M')
    
    def get_date_evenement_formattee(self):
        if self.date_evenement:
            return self.date_evenement.strftime('%d %B %Y à %H:%M')
        return None

class Commentaire(db.Model):
    """
    Commentaires sur les actualités
    """
    __tablename__ = 'commentaires'
    
    id = db.Column(db.Integer, primary_key=True)
    contenu = db.Column(db.Text, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    est_approuve = db.Column(db.Boolean, default=False)
    auteur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    actualite_id = db.Column(db.Integer, db.ForeignKey('actualites.id'), nullable=False)
    
    # Relations
    auteur = db.relationship('User', backref='commentaires')
    
    def __repr__(self):
        return f'<Commentaire {self.id} sur Actualite {self.actualite_id}>'

class PieceJointe(db.Model):
    """
    Fichiers joints aux actualités (PDF, images supplémentaires, etc.)
    """
    __tablename__ = 'pieces_jointes'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    type_fichier = db.Column(db.String(50))  # pdf, image, video, etc.
    taille = db.Column(db.Integer)  # En octets
    actualite_id = db.Column(db.Integer, db.ForeignKey('actualites.id'), nullable=False)
    
    def __repr__(self):
        return f'<PieceJointe {self.nom}>'

class CategorieActualite(db.Model):
    """
    Catégories pour organiser les actualités
    """
    __tablename__ = 'categories_actualite'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    couleur = db.Column(db.String(7), default='#0a2463')  # Code couleur hexadécimal
    
    def __repr__(self):
        return f'<CategorieActualite {self.nom}>'

