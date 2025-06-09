'''from datetime import datetime
from app.extensions import db
from flask_login import UserMixin

class Tuyau(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    matiere = db.Column(db.String(100), nullable=False)
    cycle = db.Column(db.String(20))  # 'bac' ou 'master'
    niveau = db.Column(db.Integer)  # 1 à 5
    departement = db.Column(db.String(50))  # actuariat, genie, probastate
    semestre = db.Column(db.Integer)  # 1 ou 2
    annee_academique = db.Column(db.String(20), nullable=False)  # Ex: "2022-2023"
    type_fichier = db.Column(db.String(20))  # pdf, docx, pptx
    fichier = db.Column(db.String(200))  # Chemin vers le fichier
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    
    # Relation avec l'utilisateur
    utilisateur = db.relationship('User', backref='tuyaux')
    
    def __repr__(self):
        return f'<Tuyau {self.titre}>'
        '''

from datetime import datetime
from app.extensions import db
from flask_login import UserMixin

class Tuyau(db.Model):
    __tablename__ = 'tuyaux'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    matiere = db.Column(db.String(100), nullable=False)
    cycle = db.Column(db.String(20))  # 'bac' ou 'master'
    niveau = db.Column(db.Integer)  # 1 à 5
    departement = db.Column(db.String(50))  # actuariat, genie, probastate
    semestre = db.Column(db.Integer)  # 1 ou 2
    annee_academique = db.Column(db.String(20), nullable=False)  # Ex: "2022-2023"
    type_fichier = db.Column(db.String(20))  # pdf, docx, pptx
    fichier = db.Column(db.String(200))  # Chemin vers le fichier
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    
    # Relation avec l'utilisateur
    utilisateur = db.relationship('User', backref='tuyaux')
    
    def __repr__(self):
        return f'<Tuyau {self.titre}>'
