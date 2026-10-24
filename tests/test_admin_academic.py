def test_academic_admin_forbidden_to_students(client, student, login):
    login(student)
    assert client.get("/admin/referentiel").status_code == 403
    assert client.post("/admin/referentiel/departement/nouveau", data={}).status_code == 403


def test_admin_builds_department_program_promotion(client, admin, login, db):
    from app.models import Department, Program, Promotion

    login(admin)
    assert client.post("/admin/referentiel/departement/nouveau", data={
        "code": "actu", "name": "Actuariat", "description": "",
    }).status_code == 302
    dept = Department.query.filter_by(code="ACTU").one()

    client.post("/admin/referentiel/filiere/nouveau", data={
        "code": "arisk", "name": "Analyse des risques", "cycle": "licence", "department_id": dept.id,
    })
    program = Program.query.filter_by(code="ARISK").one()

    client.post("/admin/referentiel/promotion/nouveau", data={
        "code": "bac1-arisk", "name": "BAC1 Analyse des risques", "level": "bac1",
        "academic_year": "2026-2027", "program_id": program.id, "is_active": "y",
    })
    promo = Promotion.query.filter_by(code="BAC1-ARISK").one()
    assert promo.level == "BAC1"
    assert "BAC1 Analyse des risques" in client.get("/admin/referentiel").get_data(as_text=True)


def test_duplicate_code_and_bad_year_rejected(client, admin, login, db):
    from app.models import Department

    db.session.add(Department(code="ACTU", name="Actuariat"))
    db.session.commit()
    login(admin)
    response = client.post("/admin/referentiel/departement/nouveau", data={"code": "ACTU", "name": "Autre"})
    assert "déjà utilisé" in response.get_data(as_text=True)
    response = client.post("/admin/referentiel/promotion/nouveau", data={
        "code": "X", "name": "X", "level": "M1", "academic_year": "2026-2028", "program_id": 1,
    })
    assert "La seconde année doit suivre la première" in response.get_data(as_text=True)
