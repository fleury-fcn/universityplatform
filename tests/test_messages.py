import io

from app.models import Message, MessageRecipient, Notification, StoredFile
from tests.conftest import PDF_BYTES


def _send(client, to, subject="Bonjour", body="Texte", **extra):
    data = {"to": [u.id for u in to], "subject": subject, "body": body, "promotion_id": 0}
    data.update(extra)
    return client.post("/messages/nouveau", data=data, content_type="multipart/form-data")


def test_send_read_and_notify(client, make_user, login):
    a, b = make_user("etudiant"), make_user("etudiant")
    login(a)
    assert _send(client, [b]).status_code == 302
    message = Message.query.one()
    assert Notification.query.filter_by(user_id=b.id, kind="message").count() == 1
    client.post("/deconnexion")
    login(b)
    assert "Bonjour" in client.get("/messages/").get_data(as_text=True)
    response = client.get(f"/messages/{message.id}")
    assert response.headers["Cache-Control"] == "no-store"
    assert MessageRecipient.query.filter_by(user_id=b.id).one().read_at is not None


def test_third_party_cannot_read(client, make_user, login):
    a, b, c = make_user("etudiant"), make_user("etudiant"), make_user("etudiant")
    login(a)
    _send(client, [b], attachments=(io.BytesIO(PDF_BYTES), "piece.pdf"))
    message = Message.query.one()
    stored = StoredFile.query.one()
    client.post("/deconnexion")
    login(c)
    assert client.get(f"/messages/{message.id}").status_code == 404
    assert client.get(f"/fichiers/{stored.id}/piece.pdf").status_code == 404
    client.post("/deconnexion")
    login(b)
    assert client.get(f"/fichiers/{stored.id}/piece.pdf").status_code == 200


def test_staff_broadcast_to_promotion(client, teacher, make_user, login, promotions):
    p1, p2 = promotions
    in_p1 = [make_user("etudiant", promotion_id=p1.id) for _ in range(3)]
    in_p2 = make_user("etudiant", promotion_id=p2.id)
    login(teacher)
    _send(client, [], promotion_id=p1.id)
    message = Message.query.one()
    assert {r.user_id for r in message.recipients} == {u.id for u in in_p1}
    assert in_p2.id not in {r.user_id for r in message.recipients}


def test_student_cannot_broadcast(client, student, login, promotions):
    login(student)
    _send(client, [], promotion_id=promotions[0].id)
    assert Message.query.count() == 0


def test_attachment_limits(client, make_user, login):
    a, b = make_user("etudiant"), make_user("etudiant")
    login(a)
    files = [(io.BytesIO(PDF_BYTES), f"f{i}.pdf") for i in range(4)]
    _send(client, [b], attachments=files)
    assert Message.query.count() == 0
    _send(client, [b], attachments=(io.BytesIO(b"MZ binaire"), "virus.exe"))
    assert Message.query.count() == 0 and StoredFile.query.count() == 0


def test_rate_limit(client, make_user, login, monkeypatch):
    import app.messages.routes as routes

    monkeypatch.setattr(routes, "MAX_MESSAGES_PER_HOUR", 2)
    a, b = make_user("etudiant"), make_user("etudiant")
    login(a)
    for _ in range(3):
        _send(client, [b])
    assert Message.query.count() == 2


def test_delete_is_per_user_then_purged(client, make_user, login):
    a, b = make_user("etudiant"), make_user("etudiant")
    login(a)
    _send(client, [b], attachments=(io.BytesIO(PDF_BYTES), "p.pdf"))
    message = Message.query.one()
    client.post(f"/messages/{message.id}/supprimer")
    assert Message.query.count() == 1
    client.post("/deconnexion")
    login(b)
    assert client.get(f"/messages/{message.id}").status_code == 200
    client.post(f"/messages/{message.id}/supprimer")
    assert Message.query.count() == 0
    assert StoredFile.query.count() == 0


def test_reply_prefills_sender(client, make_user, login):
    a, b = make_user("etudiant", first_name="Alice"), make_user("etudiant")
    login(a)
    _send(client, [b], subject="Question")
    message = Message.query.one()
    client.post("/deconnexion")
    login(b)
    html = client.get(f"/messages/nouveau?repondre={message.id}").get_data(as_text=True)
    assert "Re: Question" in html and f'name="to" value="{a.id}"' in html


def test_inactive_users_are_not_recipients(client, make_user, login):
    a, b = make_user("etudiant"), make_user("etudiant", is_active=False)
    login(a)
    _send(client, [b])
    assert Message.query.count() == 0


def test_directory_search(client, make_user, login):
    me = make_user("etudiant")
    make_user("enseignant", first_name="Claudine", last_name="Exemple")
    login(me)
    assert "Claudine Exemple" in client.get("/messages/annuaire?q=claud").get_data(as_text=True)
