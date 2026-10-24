"""Données de démonstration (`flask seed-demo`).

Deux catégories :
- reprises de l'ancien code ISTA (départements, filières, promotions, clubs) :
  is_demo=False mais à confirmer, voir DONNEES_A_COMPLETER.md ;
- inventées pour la démonstration : is_demo=True, affichées avec un badge DEMO.

Le script est idempotent : il peut être relancé sans créer de doublons.
"""
from datetime import date

from app.core.security import ROLE_ADMIN, ROLE_STUDENT, ROLE_TEACHER
from app.extensions import db
from app.models import Department, Program, Promotion, User

DEMO_PASSWORD = "Demo-ISTA-2026"


def current_academic_year(today=None):
    today = today or date.today()
    start = today.year if today.month >= 9 else today.year - 1
    return f"{start}-{start + 1}"


def _get_or_create(model, lookup, **values):
    obj = model.query.filter_by(**lookup).first()
    if obj is None:
        obj = model(**lookup, **values)
        db.session.add(obj)
        db.session.flush()
    return obj


# Repris de l'ancien script init_base_data.py.
DEPARTMENTS = [
    ("ACTU", "Département Actuariat", "Expertise en actuariat, assurance et gestion des risques"),
    ("GENSTAT", "Département Génie Statistique", "Statistique appliquée, sciences économiques et data science"),
    ("PROBA", "Département Probabilités et Statistique", "Modélisation probabiliste et recherche statistique avancée"),
]

PROGRAMS = [
    ("ARISK", "Analyse des Risques", "licence", "ACTU"),
    ("APRED", "Analyses Prédictives", "licence", "ACTU"),
    ("SECO", "Sciences Économiques", "licence", "GENSTAT"),
    ("SDATA", "Sciences des Données", "licence", "GENSTAT"),
    ("PROBSTATS", "Probabilités et Statistique", "licence", "PROBA"),
    ("MACTU", "Master Actuariat et Finance", "master", "ACTU"),
    ("MSAID", "Master Statistique Appliquée & Informatique Décisionnelle", "master", "GENSTAT"),
    ("MMSP", "Master Modélisation Statistique et Probabilité", "master", "PROBA"),
]

PROMOTIONS = [
    ("BAC2-ARISK-A", "BAC+2 Analyse des Risques", "BAC2", "ARISK"),
    ("BAC3-APRED-A", "BAC+3 Analyses Prédictives", "BAC3", "APRED"),
    ("BAC2-SECO-A", "BAC+2 Sciences Économiques", "BAC2", "SECO"),
    ("BAC3-SDATA-A", "BAC+3 Sciences des Données", "BAC3", "SDATA"),
    ("BAC3-PROBA-A", "BAC+3 Probabilités et Statistique", "BAC3", "PROBSTATS"),
    ("M1-ACTUFIN", "Master 1 Actuariat et Finance", "M1", "MACTU"),
    ("M1-SAID", "Master 1 Statistique Appliquée & ID", "M1", "MSAID"),
    ("M1-MSP", "Master 1 Modélisation Statistique", "M1", "MMSP"),
]


def seed_academic():
    year = current_academic_year()
    departments = {
        code: _get_or_create(Department, {"code": code}, name=name, description=desc)
        for code, name, desc in DEPARTMENTS
    }
    programs = {
        code: _get_or_create(Program, {"code": code}, name=name, cycle=cycle, department=departments[dept])
        for code, name, cycle, dept in PROGRAMS
    }
    for code, name, level, program in PROMOTIONS:
        _get_or_create(Promotion, {"code": code}, name=name, level=level, academic_year=year,
                       program=programs[program])


def seed_users():
    promotion = Promotion.query.filter_by(code="M1-SAID").first()
    accounts = [
        ("admin.demo", None, "Admin", "DEMO", ROLE_ADMIN, None),
        ("enseignant.demo", None, "Enseignant", "DEMO", ROLE_TEACHER, None),
        ("etudiant.demo", "DEMO-0001", "Étudiant", "DEMO", ROLE_STUDENT, promotion),
        ("etudiante.demo", "DEMO-0002", "Étudiante", "DEMO", ROLE_STUDENT, promotion),
    ]
    for username, matricule, first, last, role, promo in accounts:
        if User.query.filter_by(username=username).first():
            continue
        user = User(username=username, matricule=matricule, first_name=first, last_name=last, role=role,
                    promotion=promo, is_demo=True)
        user.set_password(DEMO_PASSWORD)
        db.session.add(user)
    db.session.flush()


def run():
    seed_academic()
    seed_users()
    db.session.commit()
