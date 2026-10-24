import pytest

from tests.conftest import PASSWORD


def test_anonymous_is_redirected_to_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/connexion" in response.headers["Location"]


@pytest.mark.parametrize("field", ["username", "matricule", "email"])
def test_login_with_username_matricule_or_email(client, make_user, login, field):
    user = make_user("etudiant", email="etu@example.org")
    identifier = getattr(user, field)
    response = login(identifier.lower() if field == "matricule" else identifier)
    assert response.status_code == 302
    assert client.get("/").status_code == 200


def test_wrong_password_shows_generic_message(student, login):
    response = login(student, "mauvais-mot-de-passe")
    assert response.status_code == 200
    assert "Identifiant ou mot de passe incorrect" in response.get_data(as_text=True)


def test_unknown_user_shows_same_generic_message(login):
    response = login("inconnu", "peu-importe")
    assert "Identifiant ou mot de passe incorrect" in response.get_data(as_text=True)


def test_inactive_user_cannot_login(client, make_user, login):
    user = make_user("etudiant", is_active=False)
    login(user)
    assert client.get("/").status_code == 302


def test_account_locked_after_repeated_failures(client, student, login):
    for _ in range(5):
        login(student, "mauvais")
    response = login(student, PASSWORD)
    assert response.status_code == 429
    assert client.get("/").status_code == 302


def test_login_refuses_external_next(student, client):
    response = client.post(
        "/connexion?next=https://evil.example/",
        data={"identifier": student.username, "password": PASSWORD},
    )
    assert response.headers["Location"] == "/"


def test_logout_requires_post(client, student, login):
    login(student)
    assert client.get("/deconnexion").status_code == 405
    client.post("/deconnexion")
    assert client.get("/").status_code == 302


def test_temporary_password_forces_change(client, make_user, login):
    user = make_user("etudiant", must_change_password=True)
    login(user)
    response = client.get("/")
    assert response.status_code == 302
    assert "/mot-de-passe" in response.headers["Location"]

    response = client.post("/mot-de-passe", data={
        "current_password": PASSWORD, "new_password": "Nouveau-secret-9", "confirm": "Nouveau-secret-9",
    })
    assert response.status_code == 302
    assert client.get("/").status_code == 200


def test_password_change_invalidates_other_sessions(app, student, login, client):
    other = app.test_client()
    other.post("/connexion", data={"identifier": student.username, "password": PASSWORD})
    assert other.get("/").status_code == 200

    login(student)
    client.post("/mot-de-passe", data={
        "current_password": PASSWORD, "new_password": "Nouveau-secret-9", "confirm": "Nouveau-secret-9",
    })
    assert client.get("/").status_code == 200
    assert other.get("/").status_code == 302


@pytest.mark.parametrize("password", ["court", "12345678901", "etudiant1"])
def test_weak_passwords_are_rejected(client, student, login, password):
    login(student)
    client.post("/mot-de-passe", data={"current_password": PASSWORD, "new_password": password, "confirm": password})
    client.post("/deconnexion")
    assert login(student, PASSWORD).status_code == 302  # ancien mot de passe toujours valable


def test_self_registration_disabled_by_default(client):
    assert client.get("/inscription").status_code == 404


def test_self_registration_creates_inactive_student(app, client, db):
    from app.models import Department, Program, Promotion, User

    app.config["ALLOW_SELF_REGISTRATION"] = True
    dept = Department(code="D", name="Dépt")
    prog = Program(code="P", name="Filière", department=dept)
    promo = Promotion(code="PR", name="Promo", level="BAC1", academic_year="2026-2027", program=prog)
    db.session.add_all([dept, prog, promo])
    db.session.commit()

    response = client.post("/inscription", data={
        "matricule": "ab123", "first_name": "Aline", "last_name": "Test", "email": "",
        "promotion_id": promo.id, "password": "Secret-solide-1", "confirm": "Secret-solide-1",
    })
    assert response.status_code == 302
    user = User.query.filter_by(matricule="AB123").one()
    assert user.role == "etudiant"
    assert user.is_active is False
