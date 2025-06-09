'''from datetime import datetime
from app.extensions import db

class DocumentInscription(db.Model):
    """Documents académiques"""
    __tablename__ = 'documents_inscription'
    
    id = db.Column(db.Integer, primary_key=True)
    inscription_id = db.Column(db.Integer, db.ForeignKey('inscriptions_academiques.id'), nullable=False, index=True)
    
    # Type de document (correspond aux noms dans le template)
    type_document = db.Column(db.String(50), nullable=False)  # 'diplome', 'releve', 'photo', 'cin'
    nom_original = db.Column(db.String(255))  # Nom original du fichier
    chemin_fichier = db.Column(db.String(255), nullable=False, unique=True)
    taille_fichier = db.Column(db.Integer)  # Taille en octets
    format_fichier = db.Column(db.String(10))  # Extension
    
    # Validation
    est_valide = db.Column(db.Boolean, default=False)
    date_validation = db.Column(db.DateTime)
    valide_par = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))  # Qui a validé
    
    # Métadonnées
    date_depot = db.Column(db.DateTime, default=datetime.utcnow)
    date_maj = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relations
    validateur = db.relationship('User', foreign_keys=[valide_par])
    
    def __repr__(self):
        return f'<Document {self.type_document} pour inscription {self.inscription_id}>'
        '''

from datetime import datetime
from app.extensions import db

class DocumentInscription(db.Model):
    """Documents académiques"""
    __tablename__ = 'documents_inscription'
    
    id = db.Column(db.Integer, primary_key=True)
    inscription_id = db.Column(db.Integer, db.ForeignKey('inscriptions_academiques.id'), nullable=False, index=True)
    
    # Type de document (correspond aux noms dans le template)
    type_document = db.Column(db.String(50), nullable=False)  # 'diplome', 'releve', 'photo', 'cin'
    nom_original = db.Column(db.String(255))  # Nom original du fichier
    chemin_fichier = db.Column(db.String(255), nullable=False, unique=True)
    taille_fichier = db.Column(db.Integer)  # Taille en octets
    format_fichier = db.Column(db.String(10))  # Extension
    
    # Validation
    est_valide = db.Column(db.Boolean, default=False)
    date_validation = db.Column(db.DateTime)
    valide_par = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))  # Qui a validé
    
    # Métadonnées
    date_depot = db.Column(db.DateTime, default=datetime.utcnow)
    date_maj = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relations
    validateur = db.relationship('User', foreign_keys=[valide_par])
    
    def __repr__(self):
        return f'<Document {self.type_document} pour inscription {self.inscription_id}>'
        