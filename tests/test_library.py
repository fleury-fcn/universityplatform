import io

import pytest

from app.models import Book, Notification, Reservation
from tests.conftest import PDF_BYTES


@pytest.fixture
def book(db):
    b = Book(title="Probabilités pour tous", author="A. Auteur", category="probabilite", copies_total=1)
    db.session.add(b)
    db.session.commit()
    return b


def test_reserve_and_full_workflow(client, admin, student, login, book):
    login(student)
    client.post(f"/bibliotheque/{book.id}/reserver")
    reservation = Reservation.query.one()
    assert reservation.status == "en_attente"
    client.post("/deconnexion")

    login(admin)
    client.post(f"/bibliotheque/gestion/reservations/{reservation.id}/prete")
    assert reservation.status == "prete"
    assert Notification.query.filter_by(user_id=student.id, kind="library").count() == 1
    assert book.copies_available == 0
    client.post(f"/bibliotheque/gestion/reservations/{reservation.id}/empruntee")
    assert reservation.status == "empruntee" and reservation.due_date
    client.post(f"/bibliotheque/gestion/reservations/{reservation.id}/rendue")
    assert reservation.status == "rendue"
    assert book.copies_available == 1


def test_cannot_mark_ready_without_available_copy(client, admin, make_user, login, book, db):
    a, b = make_user("etudiant"), make_user("etudiant")
    db.session.add_all([Reservation(book_id=book.id, user_id=a.id, status="empruntee"),
                        Reservation(book_id=book.id, user_id=b.id)])
    db.session.commit()
    pending = Reservation.query.filter_by(user_id=b.id).one()
    login(admin)
    client.post(f"/bibliotheque/gestion/reservations/{pending.id}/prete")
    assert pending.status == "en_attente"


def test_no_duplicate_and_limit(client, student, login, db):
    books = [Book(title=f"Livre {i}", author="X", copies_total=1) for i in range(5)]
    db.session.add_all(books)
    db.session.commit()
    login(student)
    client.post(f"/bibliotheque/{books[0].id}/reserver")
    client.post(f"/bibliotheque/{books[0].id}/reserver")
    assert Reservation.query.count() == 1
    for b in books[1:]:
        client.post(f"/bibliotheque/{b.id}/reserver")
    assert Reservation.query.count() == 3


def test_student_cancels_own_reservation_only(client, make_user, student, login, book, db):
    r = Reservation(book_id=book.id, user_id=student.id)
    db.session.add(r)
    db.session.commit()
    login(make_user("etudiant"))
    assert client.post(f"/bibliotheque/reservations/{r.id}/annuler").status_code == 404
    client.post("/deconnexion")
    login(student)
    client.post(f"/bibliotheque/reservations/{r.id}/annuler")
    assert r.status == "annulee"


def test_library_management_admin_only(client, student, teacher, login, book, db):
    r = Reservation(book_id=book.id, user_id=student.id)
    db.session.add(r)
    db.session.commit()
    for user in (student, teacher):
        login(user)
        assert client.get("/bibliotheque/gestion/reservations").status_code == 403
        assert client.post(f"/bibliotheque/gestion/reservations/{r.id}/prete").status_code == 403
        assert client.post("/bibliotheque/gestion/livres/nouveau", data={"title": "x"}).status_code == 403
        client.post("/deconnexion")


def test_admin_adds_digital_book(client, admin, student, login):
    login(admin)
    response = client.post("/bibliotheque/gestion/livres/nouveau", data={
        "title": "Cours numérique", "author": "ISTA", "category": "divers", "language": "fr",
        "copies_total": "0", "pdf": (io.BytesIO(PDF_BYTES), "livre.pdf"),
    }, content_type="multipart/form-data")
    assert response.status_code == 302
    book = Book.query.filter_by(title="Cours numérique").one()
    assert book.copies_total == 0 and book.file
    client.post("/deconnexion")
    login(student)
    assert client.get(f"/fichiers/{book.file.id}/livre.pdf").status_code == 200


def test_search(client, student, login, book):
    login(student)
    assert "Probabilités pour tous" in client.get("/bibliotheque/?q=probab").get_data(as_text=True)
    assert "Probabilités pour tous" not in client.get("/bibliotheque/?q=zzz").get_data(as_text=True)
