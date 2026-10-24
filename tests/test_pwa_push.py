import base64

import pytest

from app.models import PushSubscription

SUB = {"endpoint": "https://push.example.org/abc", "keys": {"p256dh": "cle", "auth": "secret"}}


@pytest.fixture
def push_app(app, monkeypatch):
    from cryptography.hazmat.primitives.asymmetric import ec

    key = ec.generate_private_key(ec.SECP256R1())
    raw = key.private_numbers().private_value.to_bytes(32, "big")
    app.config["VAPID_PUBLIC_KEY"] = "public"
    app.config["VAPID_PRIVATE_KEY"] = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    sent = []
    import pywebpush

    import app.services.push as push

    monkeypatch.setattr(pywebpush, "webpush", lambda **kw: sent.append(kw))

    class Immediate:
        def submit(self, fn, *args):
            fn(*args)

    monkeypatch.setattr(push, "_executor", Immediate())
    return sent


def test_offline_urls_announced_to_service_worker(client, student, login):
    login(student)
    html = client.get("/").get_data(as_text=True)
    assert 'data-offline-urls="' in html and "/emploi-du-temps/?vue=semaine" in html


def test_subscription_refused_when_push_disabled(client, student, login):
    login(student)
    assert client.post("/notifications/push/abonnement", json=SUB).status_code == 400


def test_subscribe_and_receive_push(client, push_app, student, admin, login):
    login(student)
    assert client.post("/notifications/push/abonnement", json=SUB).status_code == 200
    assert PushSubscription.query.one().user_id == student.id
    client.post("/deconnexion")

    login(admin)
    client.post("/actualites/nouvelle", data={"title": "Alerte", "body": "x", "category_id": 0,
                                              "promotion_id": 0, "is_published": "y"})
    assert len(push_app) == 1
    assert push_app[0]["subscription_info"]["endpoint"] == SUB["endpoint"]
    assert '"title": "Alerte"' in push_app[0]["data"]


def test_no_push_when_request_fails(client, push_app, student, admin, login, db):
    login(student)
    client.post("/notifications/push/abonnement", json=SUB)
    client.post("/deconnexion")
    login(admin)
    client.post("/actualites/nouvelle", data={"title": "", "body": "", "category_id": 0, "promotion_id": 0})
    assert push_app == []


def test_subscription_requires_https_endpoint(client, push_app, student, login):
    login(student)
    bad = dict(SUB, endpoint="http://insecure.example.org/x")
    assert client.post("/notifications/push/abonnement", json=bad).status_code == 400


def test_generated_vapid_key_is_usable(app):
    from cryptography.hazmat.primitives.asymmetric import ec
    from py_vapid import Vapid

    key = ec.generate_private_key(ec.SECP256R1())
    raw = base64.urlsafe_b64encode(key.private_numbers().private_value.to_bytes(32, "big")).rstrip(b"=").decode()
    vapid = Vapid.from_string(raw)
    assert vapid.sign({"aud": "https://push.example.org", "sub": "mailto:a@example.org"})
