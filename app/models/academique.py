"""
Module de gestion académique
Gère les programmes, unités d'enseignement, évaluations, notes et emplois du temps
"""
from datetime import datetime, time
from app.extensions import db
from sqlalchemy import Index, CheckConstraint


class UniteEnseignement(db.Model):
    """Unité d'Enseignement (UE) - Matière/Module"""
    __tablename__ = 'unites_enseignement'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    intitule = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Crédits et coefficients
    credits = db.Column(db.Integer, nullable=False)
    coefficient = db.Column(db.Float, nullable=False)
    
    # Organisation
    cycle = db.Column(db.String(20), nullable=False)  # licence, master, doctorat
    niveau = db.Column(db.String(20), nullable=False)  # L1, L2, L3, M1, M2
    semestre = db.Column(db.Integer, nullable=False)  # 1 ou 2
    
    departement_id = db.Column(db.Integer, db.ForeignKey('departements_academiques.id'))
    filiere_id = db.Column(db.Integer, db.ForeignKey('filieres.id'))
    
    # Volumes horaires
    volume_cm = db.Column(db.Integer, default=0)  # Cours magistral
    volume_td = db.Column(db.Integer, default=0)  # Travaux dirigés
    volume_tp = db.Column(db.Integer, default=0)  # Travaux pratiques
    volume_projet = db.Column(db.Integer, default=0)
    
    # Type et nature
    type_ue = db.Column(db.String(30))  # fondamentale, methodologie, decouverte, transversale
    nature = db.Column(db.String(30))  # obligatoire, optionnelle
    
    # Capitalisation
    est_capitalizable = db.Column(db.Boolean, default=True)
    
    # Prérequis
    prerequis = db.Column(db.Text)  # Description textuelle des prérequis
    
    # Dates et statut
    annee_academique = db.Column(db.String(20), nullable=False)
    est_active = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relations
    departement = db.relationship('DepartementAcademique', backref='unites_enseignement')
    filiere = db.relationship('Filiere', backref='unites_enseignement')
    elements_constitutifs = db.relationship('ElementConstitutif', backref='unite_enseignement', 
                                           lazy='dynamic', cascade='all, delete-orphan')
    prerequis_ues = db.relationship('PrerequisUE', foreign_keys='PrerequisUE.ue_id', 
                                    backref='ue_source', lazy='dynamic')
    evaluations = db.relationship('Evaluation', backref='unite_enseignement', lazy='dynamic')
    
    __table_args__ = (
        Index('idx_ue_code', 'code'),
        Index('idx_ue_niveau', 'niveau'),
        Index('idx_ue_filiere', 'filiere_id'),
        CheckConstraint('credits > 0', name='check_credits_positif'),
    )
    
    @property
    def volume_total(self):
        """Calcule le volume horaire total"""
        return self.volume_cm + self.volume_td + self.volume_tp + self.volume_projet
    
    def __repr__(self):
        return f'<UE {self.code} - {self.intitule}>'


class ElementConstitutif(db.Model):
    """Élément Constitutif (EC) d'une UE"""
    __tablename__ = 'elements_constitutifs'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    intitule = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    ue_id = db.Column(db.Integer, db.ForeignKey('unites_enseignement.id'), nullable=False)
    
    coefficient = db.Column(db.Float, nullable=False)
    volume_horaire = db.Column(db.Integer)
    
    type_ec = db.Column(db.String(30))  # cours, td, tp, projet
    
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EC {self.code} - {self.intitule}>'


class PrerequisUE(db.Model):
    """Relations de prérequis entre UE"""
    __tablename__ = 'prerequis_ue'
    
    id = db.Column(db.Integer, primary_key=True)
    ue_id = db.Column(db.Integer, db.ForeignKey('unites_enseignement.id'), nullable=False)
    ue_prerequis_id = db.Column(db.Integer, db.ForeignKey('unites_enseignement.id'), nullable=False)
    
    est_obligatoire = db.Column(db.Boolean, default=True)
    
    ue_prerequis = db.relationship('UniteEnseignement', foreign_keys=[ue_prerequis_id],
                                   backref='ues_dependantes')
    
    def __repr__(self):
        return f'<Prerequis UE:{self.ue_id} -> {self.ue_prerequis_id}>'


class Filiere(db.Model):
    """Filières d'étude"""
    __tablename__ = 'filieres'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    cycle = db.Column(db.String(20))  # licence, master
    departement_id = db.Column(db.Integer, db.ForeignKey('departements_academiques.id'))
    
    duree_annees = db.Column(db.Integer)  # 3 pour licence, 2 pour master
    
    responsable_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'))
    
    est_active = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    departement = db.relationship('DepartementAcademique', backref='filieres')
    responsable = db.relationship('Enseignant', backref='filieres_dirigees')
    classes = db.relationship('Classe', backref='filiere', lazy='dynamic')
    
    def __repr__(self):
        return f'<Filiere {self.code} - {self.nom}>'


class Classe(db.Model):
    """Classes/Groupes d'étudiants"""
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    
    niveau = db.Column(db.String(20), nullable=False)  # L1, L2, L3, M1, M2
    filiere_id = db.Column(db.Integer, db.ForeignKey('filieres.id'), nullable=False)
    
    annee_academique = db.Column(db.String(20), nullable=False)
    
    effectif_max = db.Column(db.Integer)
    effectif_actuel = db.Column(db.Integer, default=0)
    
    delegue_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    
    est_active = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    delegue = db.relationship('User', backref='classes_deleguees')
    etudiants = db.relationship('InscriptionClasse', backref='classe', lazy='dynamic')
    seances = db.relationship('SeanceCours', backref='classe', lazy='dynamic')
    
    def __repr__(self):
        return f'<Classe {self.code} - {self.nom}>'


class InscriptionClasse(db.Model):
    """Inscription d'un étudiant à une classe"""
    __tablename__ = 'inscriptions_classes'
    
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    
    annee_academique = db.Column(db.String(20), nullable=False)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    
    est_active = db.Column(db.Boolean, default=True)
    
    # Relations
    etudiant = db.relationship('User', backref='inscriptions_classes')
    
    __table_args__ = (
        Index('idx_inscription_etudiant', 'etudiant_id'),
        Index('idx_inscription_classe', 'classe_id'),
    )
    
    def __repr__(self):
        return f'<InscriptionClasse Etudiant:{self.etudiant_id} Classe:{self.classe_id}>'


class Evaluation(db.Model):
    """Évaluation d'une UE (examen, contrôle continu, projet, etc.)"""
    __tablename__ = 'evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    ue_id = db.Column(db.Integer, db.ForeignKey('unites_enseignement.id'), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    
    type_evaluation = db.Column(db.String(30), nullable=False)  # examen, cc, tp, projet, oral
    session = db.Column(db.String(20))  # normale, rattrapage
    
    coefficient = db.Column(db.Float, nullable=False)
    note_max = db.Column(db.Float, default=20.0)
    
    date_evaluation = db.Column(db.DateTime)
    duree_minutes = db.Column(db.Integer)
    salle = db.Column(db.String(50))
    
    annee_academique = db.Column(db.String(20), nullable=False)
    semestre = db.Column(db.Integer, nullable=False)
    
    est_publiee = db.Column(db.Boolean, default=False)
    date_publication = db.Column(db.DateTime)
    
    creee_par_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relations
    classe = db.relationship('Classe', backref='evaluations')
    creee_par = db.relationship('User', backref='evaluations_creees')
    notes = db.relationship('Note', backref='evaluation', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_evaluation_ue', 'ue_id'),
        Index('idx_evaluation_classe', 'classe_id'),
        Index('idx_evaluation_date', 'date_evaluation'),
    )
    
    def __repr__(self):
        return f'<Evaluation {self.titre} - UE:{self.ue_id}>'


class Note(db.Model):
    """Note d'un étudiant à une évaluation"""
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id'), nullable=False)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    
    note = db.Column(db.Float)
    est_absent = db.Column(db.Boolean, default=False)
    est_dispense = db.Column(db.Boolean, default=False)
    
    observations = db.Column(db.Text)
    
    saisie_par_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    date_saisie = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    est_validee = db.Column(db.Boolean, default=False)
    validee_par_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    date_validation = db.Column(db.DateTime)
    
    # Relations
    etudiant = db.relationship('User', foreign_keys=[etudiant_id], backref='notes')
    saisie_par = db.relationship('User', foreign_keys=[saisie_par_id], backref='notes_saisies')
    validee_par = db.relationship('User', foreign_keys=[validee_par_id], backref='notes_validees')
    
    __table_args__ = (
        Index('idx_note_evaluation', 'evaluation_id'),
        Index('idx_note_etudiant', 'etudiant_id'),
        CheckConstraint('note >= 0', name='check_note_positive'),
    )
    
    def __repr__(self):
        return f'<Note Eval:{self.evaluation_id} Etudiant:{self.etudiant_id} = {self.note}>'


class ReleveNotes(db.Model):
    """Relevé de notes d'un étudiant pour un semestre"""
    __tablename__ = 'releves_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    
    annee_academique = db.Column(db.String(20), nullable=False)
    semestre = db.Column(db.Integer, nullable=False)
    niveau = db.Column(db.String(20), nullable=False)
    
    moyenne_generale = db.Column(db.Float)
    credits_obtenus = db.Column(db.Integer, default=0)
    credits_totaux = db.Column(db.Integer)
    
    mention = db.Column(db.String(30))  # passable, assez_bien, bien, tres_bien
    est_valide = db.Column(db.Boolean, default=False)
    
    date_deliberation = db.Column(db.DateTime)
    delibere_par_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    
    date_generation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    etudiant = db.relationship('User', foreign_keys=[etudiant_id], backref='releves_notes')
    delibere_par = db.relationship('User', foreign_keys=[delibere_par_id], backref='releves_deliberes')
    
    __table_args__ = (
        Index('idx_releve_etudiant', 'etudiant_id'),
        Index('idx_releve_annee', 'annee_academique'),
    )
    
    def calculer_mention(self):
        """Calcule la mention selon la moyenne"""
        if self.moyenne_generale is None:
            return None
        if self.moyenne_generale >= 16:
            return 'tres_bien'
        elif self.moyenne_generale >= 14:
            return 'bien'
        elif self.moyenne_generale >= 12:
            return 'assez_bien'
        elif self.moyenne_generale >= 10:
            return 'passable'
        return None
    
    def __repr__(self):
        return f'<ReleveNotes Etudiant:{self.etudiant_id} {self.annee_academique}-S{self.semestre}>'


class Salle(db.Model):
    """Salles de cours"""
    __tablename__ = 'salles'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    
    batiment = db.Column(db.String(50))
    etage = db.Column(db.Integer)
    
    capacite = db.Column(db.Integer, nullable=False)
    type_salle = db.Column(db.String(30))  # amphi, salle_cours, labo, salle_tp
    
    equipements = db.Column(db.Text)  # Projecteur, ordinateurs, etc.
    
    est_disponible = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    seances = db.relationship('SeanceCours', backref='salle', lazy='dynamic')
    
    def __repr__(self):
        return f'<Salle {self.code} - {self.nom}>'


class SeanceCours(db.Model):
    """Séance de cours dans l'emploi du temps"""
    __tablename__ = 'seances_cours'
    
    id = db.Column(db.Integer, primary_key=True)
    
    ue_id = db.Column(db.Integer, db.ForeignKey('unites_enseignement.id'), nullable=False)
    classe_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    enseignant_id = db.Column(db.Integer, db.ForeignKey('enseignants.id'), nullable=False)
    salle_id = db.Column(db.Integer, db.ForeignKey('salles.id'))
    
    date_seance = db.Column(db.Date, nullable=False)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    
    type_seance = db.Column(db.String(20))  # cm, td, tp, projet
    
    annee_academique = db.Column(db.String(20), nullable=False)
    semestre = db.Column(db.Integer, nullable=False)
    
    statut = db.Column(db.String(20), default='planifie')  # planifie, effectue, annule, reporte
    motif_annulation = db.Column(db.Text)
    
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    creee_par_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    
    # Relations
    unite_enseignement = db.relationship('UniteEnseignement', backref='seances')
    enseignant = db.relationship('Enseignant', backref='seances')
    creee_par = db.relationship('User', backref='seances_creees')
    
    __table_args__ = (
        Index('idx_seance_date', 'date_seance'),
        Index('idx_seance_enseignant', 'enseignant_id'),
        Index('idx_seance_classe', 'classe_id'),
        Index('idx_seance_salle', 'salle_id'),
    )
    
    def __repr__(self):
        return f'<SeanceCours UE:{self.ue_id} Classe:{self.classe_id} {self.date_seance}>'
