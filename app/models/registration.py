from datetime import datetime
from app.extensions import db

class InscriptionAcademique(db.Model):
    """Données académiques des étudiants indépendantes des utilisateurs."""
    __tablename__ = 'inscriptions_academiques'
    
    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(20), unique=True, nullable=False)
    
    # Informations personnelles
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    genre = db.Column(db.String(10), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    email_institutionnel = db.Column(db.String(100))
    
    # Parcours académique
    annee_academique = db.Column(db.String(20), nullable=False)
    niveau = db.Column(db.String(20), nullable=False)
    departement = db.Column(db.String(50), nullable=False)
    specialisation = db.Column(db.String(50))
    filiere = db.Column(db.String(50))
    
    # Validation
    est_confirme = db.Column(db.Boolean, default=False)
    date_confirmation = db.Column(db.DateTime)
    est_actif = db.Column(db.Boolean, default=True)
    
    # Audit
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_mise_a_jour = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Inscription {self.matricule} - {self.niveau}>'