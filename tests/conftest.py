import pytest
from flask import g

from app import create_app
from app.extensions import db as _db


@pytest.fixture
def app(tmp_path):
    app = create_app("testing")
    app.config["UPLOAD_FOLDER"] = str(tmp_path / "uploads")

    # Le contexte d'application reste ouvert pendant le test : sans ce nettoyage, `g`
    # (et l'utilisateur chargé par Flask-Login) serait partagé entre les requêtes.
    @app.teardown_request
    def _reset_g(exc):
        for key in list(g):
            g.pop(key)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


PASSWORD = "Mot-de-passe-1"


@pytest.fixture
def make_user(db):
    from app.models import User

    counter = {"n": 0}

    def _make(role="etudiant", password=PASSWORD, **kwargs):
        counter["n"] += 1
        n = counter["n"]
        values = {
            "username": f"{role}{n}",
            "first_name": "Prénom",
            "last_name": f"Nom{n}",
            "role": role,
        }
        if role == "etudiant":
            values["matricule"] = f"MAT{n:04d}"
        values.update(kwargs)
        user = User(**values)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    return _make


@pytest.fixture
def login(client):
    def _login(user_or_identifier, password=PASSWORD, **extra):
        identifier = getattr(user_or_identifier, "username", user_or_identifier)
        return client.post("/connexion", data={"identifier": identifier, "password": password, **extra})

    return _login


@pytest.fixture
def student(make_user):
    return make_user("etudiant")


@pytest.fixture
def teacher(make_user):
    return make_user("enseignant")


@pytest.fixture
def admin(make_user):
    return make_user("admin")


@pytest.fixture
def promotions(db):
    from app.models import Department, Program, Promotion

    dept = Department(code="D", name="Département")
    prog = Program(code="P", name="Filière", department=dept)
    p1 = Promotion(code="P1", name="Promo 1", level="BAC1", academic_year="2026-2027", program=prog)
    p2 = Promotion(code="P2", name="Promo 2", level="BAC2", academic_year="2026-2027", program=prog)
    db.session.add_all([dept, prog, p1, p2])
    db.session.commit()
    return p1, p2
