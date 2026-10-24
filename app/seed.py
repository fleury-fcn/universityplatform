"""Données de démonstration (`flask seed-demo`).

Deux catégories :
- reprises de l'ancien code ISTA (départements, filières, promotions, clubs) :
  is_demo=False mais à confirmer, voir DONNEES_A_COMPLETER.md ;
- inventées pour la démonstration : is_demo=True, affichées avec un badge DEMO.

Le script est idempotent : il peut être relancé sans créer de doublons.
"""
from datetime import date, time

from app.core.security import ROLE_ADMIN, ROLE_STUDENT, ROLE_TEACHER
from app.extensions import db
from app.models import Course, Department, News, NewsCategory, Program, Promotion, Room, ScheduleEntry, User, utcnow

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


NEWS_CATEGORIES = ["Annonces", "Examens", "Vie étudiante", "Événements"]

DEMO_NEWS = [
    ("Annonces", True, "Bienvenue sur l'application de l'ISTA",
     "Cette application regroupe les actualités, l'emploi du temps, les cours, la bibliothèque, "
     "les clubs et la messagerie de l'institut.\n\nCette actualité est une donnée de démonstration : "
     "l'administration la remplacera par les vraies annonces."),
    ("Examens", False, "Exemple : calendrier des examens du semestre",
     "Exemple d'annonce d'examens. Les dates réelles seront publiées par l'administration."),
    ("Vie étudiante", False, "Exemple : réunion des délégués de promotion",
     "Exemple d'annonce de vie étudiante, à remplacer."),
]


def seed_news():
    categories = {}
    for position, name in enumerate(NEWS_CATEGORIES):
        categories[name] = _get_or_create(NewsCategory, {"name": name}, position=position)
    author = User.query.filter_by(username="admin.demo").first()
    if author is None:
        return
    for category, pinned, title, body in DEMO_NEWS:
        _get_or_create(News, {"title": title}, body=body, category=categories[category], author=author,
                       is_published=True, is_pinned=pinned, published_at=utcnow(), is_demo=True)


DEMO_ROOMS = [
    ("DEMO-AMPHI", "Amphithéâtre (DEMO)", "amphi", 150),
    ("DEMO-S1", "Salle 1 (DEMO)", "salle", 45),
    ("DEMO-LABO", "Laboratoire informatique (DEMO)", "labo", 30),
    ("DEMO-BIB", "Bibliothèque (DEMO)", "bibliotheque", 60),
]

# Intitulés repris des UE de l'ancien code (Master SAID) ; horaires inventés.
DEMO_SESSIONS = [
    (0, time(8), time(10), "Génie logiciel avancé", "CM", "DEMO-S1"),
    (1, time(10), time(12), "Architecture BI & Big Data", "CM", "DEMO-AMPHI"),
    (2, time(14), time(16), "Architecture BI & Big Data", "TP", "DEMO-LABO"),
    (3, time(8), time(10), "Génie logiciel avancé", "TD", "DEMO-S1"),
    (4, time(10), time(12), "Méthodologie de recherche", "CM", "DEMO-AMPHI"),
]


def seed_rooms_and_schedule():
    rooms = {
        code: _get_or_create(Room, {"code": code}, name=name, kind=kind, capacity=capacity, is_demo=True)
        for code, name, kind, capacity in DEMO_ROOMS
    }
    promotion = Promotion.query.filter_by(code="M1-SAID").first()
    teacher = User.query.filter_by(username="enseignant.demo").first()
    if promotion is None:
        return
    for weekday, start, end, title, kind, room in DEMO_SESSIONS:
        _get_or_create(
            ScheduleEntry, {"promotion_id": promotion.id, "weekday": weekday, "start_time": start},
            end_time=end, title=title, kind=kind, room=rooms[room], teacher=teacher, is_demo=True,
        )


# UE reprises de l'ancien script init_base_data.py (crédits et semestres à confirmer),
# plus deux cours de démonstration pour le Master SAID (cohérents avec l'emploi du temps).
DEMO_COURSES = [
    ("ARISK201", "Mathématiques de l'assurance", "BAC2-ARISK-A", 1, 6),
    ("APRED301", "Apprentissage statistique", "BAC3-APRED-A", 1, 5),
    ("SECO210", "Politiques macroéconomiques", "BAC2-SECO-A", 2, 4),
    ("SDATA320", "Informatique décisionnelle", "BAC3-SDATA-A", 2, 5),
    ("PROB330", "Processus aléatoires avancés", "BAC3-PROBA-A", 2, 6),
    ("MACTU510", "Gestion actif-passif", "M1-ACTUFIN", 1, 6),
    ("MSAID520", "Architecture BI & Big Data", "M1-SAID", 1, 5),
    ("MMSP530", "Théorie avancée des probabilités", "M1-MSP", 1, 5),
    ("SAID401", "Génie logiciel avancé", "M1-SAID", 1, 4),
    ("SAID410", "Méthodologie de recherche", "M1-SAID", 1, 3),
]


def seed_courses():
    teacher = User.query.filter_by(username="enseignant.demo").first()
    for code, title, promotion_code, semester, credits in DEMO_COURSES:
        promotion = Promotion.query.filter_by(code=promotion_code).first()
        if promotion:
            _get_or_create(Course, {"code": code, "promotion_id": promotion.id}, title=title, semester=semester,
                           credits=credits, is_demo=True,
                           teacher=teacher if promotion_code == "M1-SAID" else None)


def run():
    seed_academic()
    seed_users()
    seed_news()
    seed_rooms_and_schedule()
    seed_courses()
    db.session.commit()
