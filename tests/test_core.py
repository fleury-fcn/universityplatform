def test_home_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "ISTA" in response.get_data(as_text=True)


def test_security_headers(client):
    response = client.get("/")
    csp = response.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    assert "'unsafe-inline'" not in csp
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_inline_script_uses_csp_nonce(client):
    response = client.get("/")
    html = response.get_data(as_text=True)
    nonce = response.headers["Content-Security-Policy"].split("'nonce-")[1].split("'")[0]
    assert f'nonce="{nonce}"' in html


def test_language_switch_sets_cookie_and_refuses_external_redirect(client):
    response = client.get("/langue/en?next=https://evil.example/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    assert "lang=en" in response.headers["Set-Cookie"]
    assert client.get("/langue/xx").status_code == 404


def test_french_is_default_language(client):
    html = client.get("/", headers={"Accept-Language": "en"}).get_data(as_text=True)
    assert '<html lang="fr">' in html


def test_unknown_page_uses_error_template(client):
    response = client.get("/nexiste-pas")
    assert response.status_code == 404
    assert "Page introuvable" in response.get_data(as_text=True)


def test_pwa_endpoints(client):
    sw = client.get("/sw.js")
    assert sw.status_code == 200
    assert sw.mimetype == "text/javascript"
    assert "/hors-ligne" in sw.get_data(as_text=True)
    manifest = client.get("/manifest.webmanifest")
    assert manifest.status_code == 200
    assert manifest.get_json()["short_name"] == "ISTA"
    assert client.get("/hors-ligne").status_code == 200


def test_health(client):
    assert client.get("/sante").get_json() == {"status": "ok"}


def test_csrf_is_enforced_outside_tests():
    from app import create_app

    app = create_app("testing")
    app.config["WTF_CSRF_ENABLED"] = True

    @app.route("/_post", methods=["POST"])
    def _post():
        return "ok"

    assert app.test_client().post("/_post").status_code == 400


def test_production_requires_secret_key(monkeypatch):
    import pytest

    from app import create_app
    from app.config import ProductionConfig

    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", None)
    with pytest.raises(RuntimeError):
        create_app("production")
