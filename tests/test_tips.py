import io

from app.models import Notification, Tip, TipReport, TipVote
from tests.conftest import PDF_BYTES

BODY = "Un conseil suffisamment long pour être accepté."


def _share(client, title="Bon plan", **extra):
    data = {"title": title, "category": "cours", "course_id": 0, "body": BODY}
    data.update(extra)
    return client.post("/tuyaux/nouveau", data=data, content_type="multipart/form-data")


def test_student_tip_requires_moderation(client, admin, student, make_user, login):
    login(student)
    _share(client, "Mon tuyau")
    tip = Tip.query.one()
    assert tip.status == "en_attente"
    assert Notification.query.filter_by(user_id=admin.id, kind="moderation").count() == 1
    client.post("/deconnexion")

    other = make_user("etudiant")
    login(other)
    assert "Mon tuyau" not in client.get("/tuyaux/").get_data(as_text=True)
    assert client.get(f"/tuyaux/{tip.id}").status_code == 404
    client.post("/deconnexion")

    login(admin)
    client.post(f"/tuyaux/{tip.id}/moderer/publier", data={"note": ""})
    assert tip.status == "publie"
    assert Notification.query.filter_by(user_id=student.id, kind="moderation").count() == 1
    client.post("/deconnexion")

    login(other)
    assert "Mon tuyau" in client.get("/tuyaux/").get_data(as_text=True)


def test_teacher_tip_published_directly(client, teacher, login):
    login(teacher)
    _share(client)
    assert Tip.query.one().status == "publie"


def test_rejected_tip_shows_reason_to_author(client, admin, student, login):
    login(student)
    _share(client)
    tip = Tip.query.one()
    client.post("/deconnexion")
    login(admin)
    client.post(f"/tuyaux/{tip.id}/moderer/refuser", data={"note": "Hors sujet"})
    client.post("/deconnexion")
    login(student)
    assert "Hors sujet" in client.get(f"/tuyaux/{tip.id}").get_data(as_text=True)


def test_vote_toggle_and_no_self_vote(client, teacher, student, login):
    login(teacher)
    _share(client)
    tip = Tip.query.one()
    client.post(f"/tuyaux/{tip.id}/utile")
    assert TipVote.query.count() == 0
    client.post("/deconnexion")
    login(student)
    client.post(f"/tuyaux/{tip.id}/utile")
    assert TipVote.query.count() == 1
    client.post(f"/tuyaux/{tip.id}/utile")
    assert TipVote.query.count() == 0


def test_report_notifies_admins_once(client, admin, teacher, student, login):
    login(teacher)
    _share(client)
    tip = Tip.query.one()
    client.post("/deconnexion")
    login(student)
    client.post(f"/tuyaux/{tip.id}/signaler", data={"reason": "Contenu faux"})
    client.post(f"/tuyaux/{tip.id}/signaler", data={"reason": "Encore"})
    assert TipReport.query.count() == 1
    assert Notification.query.filter_by(user_id=admin.id, kind="moderation").count() == 1


def test_moderation_admin_only(client, student, teacher, login):
    login(teacher)
    _share(client)
    tip = Tip.query.one()
    client.post("/deconnexion")
    login(student)
    assert client.get("/tuyaux/moderation").status_code == 403
    assert client.post(f"/tuyaux/{tip.id}/moderer/refuser", data={}).status_code == 403
    assert client.post(f"/tuyaux/{tip.id}/supprimer").status_code == 403


def test_attachment_of_pending_tip_is_private(client, student, make_user, login):
    login(student)
    _share(client, attachment=(io.BytesIO(PDF_BYTES), "fiche.pdf"))
    tip = Tip.query.one()
    assert client.get(f"/fichiers/{tip.file.id}/fiche.pdf").status_code == 200
    client.post("/deconnexion")
    login(make_user("etudiant"))
    assert client.get(f"/fichiers/{tip.file.id}/fiche.pdf").status_code == 404


def test_tip_body_min_length(client, student, login):
    login(student)
    _share(client, body="court")
    assert Tip.query.count() == 0
