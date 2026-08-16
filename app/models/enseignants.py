"""
Module de gestion des enseignants
Gère les informations, documents, affectations et historiques des enseignants
"""
from datetime import datetime
from app.extensions import db
from sqlalchemy import Index


class Enseignant(db.Model):
    """Modèle représentant un enseignant de l'établissement"""
    __tablename__ = 'enseignants'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Informations personnelles
    matricule = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    genre = db.Column(db.String(10))
    date_naissance = db.Column(db.Date)
    lieu_naissance = db.Column(db.String(100))
    nationalite = db.Column(db.String(50))
    
    # Coordonnées
    email_professionnel = db.Column(db.String(120), unique=True, nullable=False, index=True)
    email_personnel = db.Column(db.String(120))
    telephone_mobile = db.Column(db.String(20))
    telephone_fixe = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    ville = db.Column(db.String(50))
    code_postal = db.Column(db.String(10))
    
    # Informations professionnelles
    grade = db.Column(db.String(50))  # Professeur, Maître Assistant, Assistant, Vacataire
    specialite = db.Column(db.String(100), nullable=False)
    departement_id = db.Column(db.Integer, db.ForeignKey('departements_academiques.id'))
    type_emploi = db.Column(db.String(20))  # temps_plein, temps_partiel, vacataire
    statut = db.Column(db.String(20), default='actif')  # actif, inactif, suspendu, retraité
    
    # Disponibilité et charge horaire
    heures_disponibles = db.Column(db.Integer)  # Heures par semaine
    charge_horaire_totale = db.Column(db.Integer, default=0)  # Heures affectées
    volume_horaire_annuel = db.Column(db.Integer)  # Volume contractuel
    
    # Dates
    date_recrutement = db.Column(db.Date)
    date_fin_contrat = db.Column(db.Date)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Lien avec le compte utilisateur
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), unique=True)
    
    # Photo de profil
    photo = db.Column(db.String(255))
    
    # Relations
    user = db.relationship('User', backref=db.backref('enseignant', uselist=False))
    departement = db.relationship(
        'DepartementAcademique',
        foreign_keys=[departement_id],
        back_populates='enseignants'
    )
    documents = db.relationship('DocumentEnseignant', backref='enseignant', lazy='dynamic', cascade='all, delete-orphan')
    affectations = db.relationship('AffectationCours', backref='enseignant', lazy='dynamic', cascade='all, delete-orphan')
    presences = db.relationship('PresenceEnseignant', backref='enseignant', lazy='dynamic', cascade='all, delete-orphan')
    disponibilites = db.relationship('DisponibiliteEnseignant', backref='enseignant', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_enseignant_email', 'email_professionnel'),
        Index('idx_enseignant_statut', 'statut'),
        Index('idx_enseignant_departement', 'departement_id'),
    )
    
    @property
    def nom_complet(self):
        """Retourne le nom complet"""
        return f"{self.prenom} {self.nom}"
    
    @property
    def charge_horaire_pourcent(self):
        """Calcule le pourcentage de charge horaire"""
        if self.volume_horaire_annuel and self.volume_horaire_annuel > 0:
            return round((self.charge_horaire_totale / self.volume_horaire_annuel) * 100, 2)
        return 0
    
    @property
    def est_surcharge(self):
        """Vérifie si l'enseignant est en surcharge"""
        return self.charge_horaire_totale > self.volume_horaire_annuel if self.volume_horaire_annuel else False
    
    @property
    def est_sous_charge(self):
        """Vérifie si l'enseignant est en sous-charge"""
        if self.volume_horaire_annuel:
            return self.charge_horaire_totale < (self.volume_horaire_annuel * 0.8)
        return False
    
    def calculer_charge_horaire(self):
        """Calcule la charge horaire totale à partir des affectations"""
        total = sum(aff.volume_horaire for aff in self.affectations if aff.est_active)
        self.charge_horaire_totale = total
        return total
    
    def __repr__(self):
        return f'<Enseignant {self.matricule} - {self.nom_complet}>'


class DocumentEnseignant(db.Model):
    """Documents associés aux enseignants (CV, diplômes, contrats, etc.)"""
    __tablename__ = 'documents_enseignants'
    
    id = db.Column(db.Integer, primary_key=True)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'), nullable=False)
    
    type_document = db.Column(db.String(50), nullable=False)  # cv, diplome, contrat, attestation, etc.
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    nom_fichier = db.Column(db.String(255), nullable=False)
    chemin_fichier = db.Column(db.String(500), nullable=False)
    taille_fichier = db.Column(db.Integer)  # en octets
    
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    date_expiration = db.Column(db.Date)  # Pour les documents temporaires
    
    ajoute_par_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    ajoute_par = db.relationship('User', backref='documents_enseignants_ajoutes')
    
    def __repr__(self):
        return f'<DocumentEnseignant {self.type_document} - {self.titre}>'


class AffectationCours(db.Model):
    """Affectation des enseignants aux cours et classes"""
    __tablename__ = 'affectations_cours'
    
    id = db.Column(db.Integer, primary_key=True)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'), nullable=False)
    unite_enseignement_id = db.Column(db.Integer, db.ForeignKey('unites_enseignement.id'), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    
    annee_academique = db.Column(db.String(20), nullable=False)  # 2024-2025
    semestre = db.Column(db.Integer, nullable=False)  # 1 ou 2
    
    type_intervention = db.Column(db.String(20))  # cours, td, tp, projet
    volume_horaire = db.Column(db.Integer, nullable=False)  # Heures par semestre
    
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date)
    est_active = db.Column(db.Boolean, default=True)
    
    date_affectation = db.Column(db.DateTime, default=datetime.utcnow)
    affecte_par_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    
    # Relations
    unite_enseignement = db.relationship('UniteEnseignement', backref='affectations')
    classe = db.relationship('Classe', backref='affectations')
    affecte_par = db.relationship('User', backref='affectations_creees')
    
    __table_args__ = (
        Index('idx_affectation_enseignant', 'enseignant_id'),
        Index('idx_affectation_ue', 'unite_enseignement_id'),
        Index('idx_affectation_annee', 'annee_academique'),
    )
    
    def __repr__(self):
        return f'<AffectationCours Ens:{self.enseignant_id} UE:{self.unite_enseignement_id}>'


class PresenceEnseignant(db.Model):
    """Gestion des présences et absences des enseignants"""
    __tablename__ = 'presences_enseignants'
    
    id = db.Column(db.Integer, primary_key=True)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'), nullable=False)
    seance_id = db.Column(db.Integer, db.ForeignKey('seances_cours.id'), nullable=False)
    
    date_seance = db.Column(db.Date, nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    
    statut = db.Column(db.String(20), default='present')  # present, absent, retard, justifie
    heure_arrivee = db.Column(db.Time)
    heure_depart = db.Column(db.Time)
    
    justification = db.Column(db.Text)
    document_justificatif = db.Column(db.String(255))
    
    enregistre_par_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    date_enregistrement = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    seance = db.relationship('SeanceCours', backref='presences')
    enregistre_par = db.relationship('User', backref='presences_enregistrees')
    
    __table_args__ = (
        Index('idx_presence_enseignant', 'enseignant_id'),
        Index('idx_presence_date', 'date_seance'),
    )
    
    def __repr__(self):
        return f'<PresenceEnseignant {self.enseignant_id} - {self.date_seance}>'


class DisponibiliteEnseignant(db.Model):
    """Disponibilités hebdomadaires des enseignants pour la planification"""
    __tablename__ = 'disponibilites_enseignants'
    
    id = db.Column(db.Integer, primary_key=True)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'), nullable=False)
    
    jour_semaine = db.Column(db.Integer, nullable=False)  # 1=Lundi, 7=Dimanche
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    
    type_disponibilite = db.Column(db.String(20), default='disponible')  # disponible, indisponible, prefere
    
    annee_academique = db.Column(db.String(20))
    semestre = db.Column(db.Integer)
    
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_disponibilite_enseignant', 'enseignant_id'),
        Index('idx_disponibilite_jour', 'jour_semaine'),
    )
    
    def __repr__(self):
        return f'<DisponibiliteEnseignant {self.enseignant_id} - Jour {self.jour_semaine}>'


class DepartementAcademique(db.Model):
    """Départements académiques de l'établissement"""
    __tablename__ = 'departements_academiques'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    responsable_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'))
    
    est_actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    responsable = db.relationship(
        'Enseignant',
        foreign_keys=[responsable_id],
        backref='departements_diriges',
        post_update=True
    )
    enseignants = db.relationship(
        'Enseignant',
        foreign_keys='Enseignant.departement_id',
        back_populates='departement',
        lazy='dynamic'
    )
    
    def __repr__(self):
        return f'<DepartementAcademique {self.code} - {self.nom}>'
