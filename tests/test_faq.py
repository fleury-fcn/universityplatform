import pytest

from app.faq.search import normalize, rank
from app.models import FaqEntry


@pytest.fixture
def entries(db):
    items = [
        FaqEntry(question="J'ai oublié mon mot de passe. Que faire ?", answer="Allez au secrétariat.",
                 keywords="perdu connexion"),
        FaqEntry(question="Comment réserver un livre ?", answer="Ouvrez la bibliothèque.", keywords="emprunter"),
        FaqEntry(question="Où voir mes notes ?", answer="Rubrique Notes.", keywords="résultats"),
    ]
    db.session.add_all(items)
    db.session.commit()
    return items


def test_normalize_removes_accents_and_stopwords():
    assert normalize("Comment réserver un Livre ?") == ["reserver", "livre"]


@pytest.mark.parametrize("query,expected", [
    ("mot de passe perdu", 0),
    ("je veux emprunter des livres", 1),
    ("RESULTATS d'examen", 2),
    ("reservation bibliotheque", 1),
])
def test_rank_finds_best_answer(entries, query, expected):
    assert rank(entries, query)[0] is entries[expected]


def test_rank_without_match(entries):
    assert rank(entries, "football") == []
    assert rank(entries, "le la les") == []


def test_faq_page_search(client, student, login, entries):
    login(student)
    html = client.get("/faq/?q=mot+de+passe+oublie").get_data(as_text=True)
    assert "Réponses proposées" in html and "secrétariat" in html


def test_faq_management_admin_only(client, student, admin, login):
    login(student)
    assert client.post("/faq/nouvelle", data={"question": "Q", "answer": "R", "category": "C"}).status_code == 403
    client.post("/deconnexion")
    login(admin)
    client.post("/faq/nouvelle", data={"question": "Horaires ?", "answer": "8h-17h", "category": "Vie pratique"})
    assert FaqEntry.query.filter_by(question="Horaires ?").one().category == "Vie pratique"
