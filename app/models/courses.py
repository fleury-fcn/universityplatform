from datetime import datetime
from ..extensions import db
from flask_login import UserMixin

class Cours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    titre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer)
    cycle = db.Column(db.String(20))  # 'bac' ou 'master'
    annee = db.Column(db.Integer)  # 1 à 5
    departement = db.Column(db.String(50))  # actuariat, genie, probastate
    parcours = db.Column(db.String(50))  # said, psm, af (pour master)
    semestre = db.Column(db.Integer)  # 1 ou 2
    specialisation = db.Column(db.String(50))
    horaire = db.Column(db.String(100))
    lieu = db.Column(db.String(100))
    fichier = db.Column(db.String(200))  # Chemin vers le fichier PDF
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    professeur_id = db.Column(db.Integer, db.ForeignKey('professeur.id'))
    ressources = db.relationship('Ressource', backref='cours', lazy=True)

class Ressource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20))  # pdf, code, etc.
    taille = db.Column(db.String(20))
    chemin = db.Column(db.String(200), nullable=False)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    cours_id = db.Column(db.Integer, db.ForeignKey('cours.id'), nullable=False)

class Professeur(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(200))  # Chemin vers l'image
    cours = db.relationship('Cours', backref='professeur', lazy=True)