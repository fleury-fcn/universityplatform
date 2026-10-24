from app.models import News, Notification


def _publish(client, **data):
    payload = {"title": "Titre", "body": "Texte", "category_id": 0, "promotion_id": 0, "is_published": "y"}
    payload.update(data)
    return client.post("/actualites/nouvelle", data=payload)


def test_only_admin_can_manage_news(client, student, teacher, login):
    for user in (student, teacher):
        login(user)
        assert client.get("/actualites/gestion").status_code == 403
        assert _publish(client).status_code == 403
        client.post("/deconnexion")


def test_publishing_notifies_everyone_once(client, admin, student, teacher, login, db):
    login(admin)
    assert _publish(client, title="Rentrée").status_code == 302
    item = News.query.filter_by(title="Rentrée").one()
    assert Notification.query.filter_by(user_id=student.id).count() == 1
    assert Notification.query.filter_by(user_id=teacher.id).count() == 1
    assert Notification.query.filter_by(user_id=admin.id).count() == 0  # pas l'auteur

    # Une modification ne renvoie pas de notification.
    client.post(f"/actualites/{item.id}/modifier", data={
        "title": "Rentrée (modifié)", "body": "Texte", "category_id": 0, "promotion_id": 0, "is_published": "y",
    })
    assert Notification.query.filter_by(user_id=student.id).count() == 1


def test_draft_is_hidden_and_not_notified(client, admin, student, login, db):
    login(admin)
    client.post("/actualites/nouvelle", data={"title": "Brouillon", "body": "x", "category_id": 0, "promotion_id": 0})
    item = News.query.filter_by(title="Brouillon").one()
    assert Notification.query.count() == 0
    client.post("/deconnexion")
    login(student)
    assert client.get(f"/actualites/{item.id}").status_code == 404
    assert "Brouillon" not in client.get("/actualites/").get_data(as_text=True)


def test_promotion_targeted_news(client, admin, make_user, login, promotions, db):
    p1, p2 = promotions
    in_p1 = make_user("etudiant", promotion_id=p1.id)
    in_p2 = make_user("etudiant", promotion_id=p2.id)
    login(admin)
    _publish(client, title="Pour P1", promotion_id=p1.id)
    item = News.query.filter_by(title="Pour P1").one()
    assert Notification.query.filter_by(user_id=in_p1.id).count() == 1
    assert Notification.query.filter_by(user_id=in_p2.id).count() == 0
    client.post("/deconnexion")

    login(in_p2)
    assert client.get(f"/actualites/{item.id}").status_code == 404
    client.post("/deconnexion")
    login(in_p1)
    assert client.get(f"/actualites/{item.id}").status_code == 200


def test_reading_news_marks_notification_read(client, admin, student, login, db):
    login(admin)
    _publish(client, title="À lire")
    item = News.query.filter_by(title="À lire").one()
    client.post("/deconnexion")
    login(student)
    assert ">1<" in client.get("/actualites/").get_data(as_text=True)  # pastille
    client.get(f"/actualites/{item.id}")
    assert Notification.query.filter_by(user_id=student.id, read_at=None).count() == 0


def test_news_body_is_escaped(client, admin, student, login, db):
    login(admin)
    _publish(client, title="XSS", body="<script>alert(1)</script>")
    item = News.query.filter_by(title="XSS").one()
    html = client.get(f"/actualites/{item.id}").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_latest_news_on_home(client, admin, student, login, db):
    login(admin)
    _publish(client, title="Sur l'accueil")
    client.post("/deconnexion")
    login(student)
    assert "Sur l&#39;accueil" in client.get("/").get_data(as_text=True)


def test_notifications_are_private(client, admin, student, make_user, login, db):
    login(admin)
    _publish(client, title="Privée")
    notification = Notification.query.filter_by(user_id=student.id).one()
    client.post("/deconnexion")
    login(make_user("etudiant"))
    assert client.get(f"/notifications/{notification.id}").status_code == 404
