import io

import pytest


@pytest.mark.parametrize("role", ["etudiant", "enseignant"])
def test_admin_area_forbidden_to_non_admins(client, make_user, login, role):
    login(make_user(role))
    assert client.get("/admin/").status_code == 403
    assert client.get("/admin/utilisateurs").status_code == 403
    assert client.post("/admin/utilisateurs/nouveau", data={}).status_code == 403


def test_admin_area_requires_login(client):
    assert client.get("/admin/utilisateurs").status_code == 302


def test_admin_creates_user_with_temporary_password(client, admin, login, db):
    from app.models import User

    login(admin)
    response = client.post("/admin/utilisateurs/nouveau", data={
        "role": "etudiant", "first_name": "Jean", "last_name": "Test", "matricule": "x42",
        "promotion_id": 0, "is_active": "y",
    })
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    user = User.query.filter_by(matricule="X42").one()
    assert user.username == "x42"
    assert user.must_change_password
    html = response.get_data(as_text=True)
    password = html.split('class="secret">')[1].split("<")[0]
    assert user.check_password(password)


def test_student_requires_matricule(client, admin, login):
    login(admin)
    response = client.post("/admin/utilisateurs/nouveau", data={
        "role": "etudiant", "first_name": "Jean", "last_name": "Test", "promotion_id": 0,
    })
    assert "Le matricule est obligatoire" in response.get_data(as_text=True)


def test_admin_cannot_demote_self(client, admin, login, db):
    login(admin)
    client.post(f"/admin/utilisateurs/{admin.id}", data={
        "role": "etudiant", "first_name": "A", "last_name": "B", "username": admin.username,
        "matricule": "M1", "promotion_id": 0, "is_active": "y",
    })
    db.session.refresh(admin)
    assert admin.role == "admin"


def test_reset_password(client, admin, student, login, db):
    login(admin)
    response = client.post(f"/admin/utilisateurs/{student.id}/mot-de-passe")
    assert response.status_code == 200
    db.session.refresh(student)
    assert student.must_change_password
    assert client.post(f"/admin/utilisateurs/{admin.id}/mot-de-passe").status_code == 400


def test_csv_import_creates_accounts_and_returns_credentials(client, admin, login, db):
    from app.models import User

    login(admin)
    csv_data = "matricule;prenom;nom;email;promotion;role\nA1;Ana;Un;;;\nT1;Tom;Deux;t@example.org;;enseignant\n"
    response = client.post("/admin/utilisateurs/import", data={
        "file": (io.BytesIO(csv_data.encode()), "comptes.csv"),
    }, content_type="multipart/form-data")
    assert response.mimetype == "text/csv"
    body = response.get_data(as_text=True)
    assert "a1;A1;Ana;Un;" in body
    assert User.query.filter_by(matricule="T1").one().role == "enseignant"


def test_csv_import_is_all_or_nothing(client, admin, login, db):
    from app.models import User

    login(admin)
    csv_data = "matricule;prenom;nom;role\nB1;Ana;Un;etudiant\nB2;Bob;Deux;pirate\n"
    response = client.post("/admin/utilisateurs/import", data={
        "file": (io.BytesIO(csv_data.encode()), "comptes.csv"),
    }, content_type="multipart/form-data")
    assert "rôle inconnu" in response.get_data(as_text=True)
    assert User.query.filter_by(matricule="B1").first() is None


def test_deactivating_user_logs_them_out(app, client, admin, student, login, db):
    other = app.test_client()
    other.post("/connexion", data={"identifier": student.username, "password": "Mot-de-passe-1"})
    assert other.get("/").status_code == 200
    login(admin)
    client.post(f"/admin/utilisateurs/{student.id}", data={
        "role": "etudiant", "first_name": "P", "last_name": "N", "matricule": student.matricule,
        "promotion_id": 0,
    })
    assert other.get("/").status_code == 302


def test_profile_shows_student_information(client, student, login):
    login(student)
    response = client.get("/profil")
    assert student.matricule in response.get_data(as_text=True)
    assert response.headers["Cache-Control"] == "no-store"


def test_profile_email_must_be_unique(client, make_user, student, login, db):
    make_user("etudiant", email="pris@example.org")
    login(student)
    response = client.post("/profil/modifier", data={"email": "pris@example.org", "locale": "fr"})
    assert "déjà utilisé" in response.get_data(as_text=True)
