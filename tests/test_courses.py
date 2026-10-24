import io
import zipfile

import pytest

from app.models import Course, Notification, Resource, StoredFile
from tests.conftest import PDF_BYTES


def _upload(client, course, content=PDF_BYTES, filename="cours.pdf", kind="support"):
    return client.post(f"/cours/{course.id}", data={
        "title": "Chapitre 1", "kind": kind, "academic_year": "",
        "file": (io.BytesIO(content), filename),
    }, content_type="multipart/form-data")


def test_student_sees_courses_of_own_promotion_only(client, make_user, login, course, promotions):
    login(make_user("etudiant", promotion_id=promotions[1].id))
    assert "Statistique descriptive" not in client.get("/cours/").get_data(as_text=True)
    assert client.get(f"/cours/{course.id}").status_code == 404
    client.post("/deconnexion")
    login(make_user("etudiant", promotion_id=promotions[0].id))
    assert "Statistique descriptive" in client.get("/cours/").get_data(as_text=True)
    assert client.get(f"/cours/{course.id}").status_code == 200


def test_teacher_uploads_and_students_are_notified(client, teacher, make_user, login, course, app):
    student = make_user("etudiant", promotion_id=course.promotion_id)
    login(teacher)
    assert _upload(client, course).status_code == 302
    resource = Resource.query.one()
    assert resource.file.mime_type == "application/pdf"
    assert Notification.query.filter_by(user_id=student.id).count() == 1

    client.post("/deconnexion")
    login(student)
    response = client.get(f"/fichiers/{resource.file.id}/cours.pdf")
    assert response.status_code == 200
    assert response.data == PDF_BYTES
    assert "private" in response.headers["Cache-Control"]


def test_student_cannot_upload(client, make_user, login, course):
    login(make_user("etudiant", promotion_id=course.promotion_id))
    _upload(client, course)
    assert Resource.query.count() == 0


def test_other_teacher_cannot_upload_or_delete(client, make_user, teacher, login, course):
    login(teacher)
    _upload(client, course)
    resource = Resource.query.one()
    client.post("/deconnexion")
    login(make_user("enseignant"))
    _upload(client, course)
    assert Resource.query.count() == 1
    assert client.post(f"/cours/ressources/{resource.id}/supprimer").status_code == 403


def test_file_of_other_promotion_is_not_downloadable(client, teacher, make_user, login, course, promotions):
    login(teacher)
    _upload(client, course)
    stored = StoredFile.query.one()
    client.post("/deconnexion")
    login(make_user("etudiant", promotion_id=promotions[1].id))
    assert client.get(f"/fichiers/{stored.id}/x.pdf").status_code == 404


def test_anonymous_cannot_download(client, teacher, login, course):
    login(teacher)
    _upload(client, course)
    stored = StoredFile.query.one()
    client.post("/deconnexion")
    assert client.get(f"/fichiers/{stored.id}/x.pdf").status_code == 302


@pytest.mark.parametrize("content,filename", [
    (b"<html><script>alert(1)</script></html>", "faux.pdf"),   # contenu qui ne correspond pas
    (b"MZ\x90\x00binaire", "programme.exe"),                     # extension interdite
    (b"PK\x03\x04pas un vrai docx", "faux.docx"),                # zip invalide
    (b"", "vide.pdf"),                                           # fichier vide
])
def test_invalid_files_are_rejected(client, teacher, login, course, content, filename):
    login(teacher)
    response = _upload(client, course, content, filename)
    assert response.status_code == 200
    assert Resource.query.count() == 0
    assert StoredFile.query.count() == 0


def test_valid_docx_is_accepted(client, teacher, login, course):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
        zf.writestr("word/document.xml", "<doc/>")
    login(teacher)
    assert _upload(client, course, buf.getvalue(), "td.docx").status_code == 302


def test_size_limit(client, teacher, login, course, app):
    app.config["MAX_CONTENT_LENGTH"] = 1024
    login(teacher)
    response = _upload(client, course, PDF_BYTES + b"x" * 2048)
    assert response.status_code in (200, 413)
    assert Resource.query.count() == 0


def test_stored_name_is_random_and_original_name_sanitized(client, teacher, login, course, app):
    import os

    login(teacher)
    _upload(client, course, filename="../../etc/passwd.pdf")
    stored = StoredFile.query.one()
    assert "/" not in stored.original_name and ".." not in stored.original_name
    assert stored.stored_name != stored.original_name
    assert os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], "resource", stored.stored_name))


def test_course_management_admin_only(client, teacher, login, course):
    login(teacher)
    assert client.get("/cours/gestion").status_code == 403
    assert client.post(f"/cours/{course.id}/supprimer").status_code == 403


def test_admin_creates_course(client, admin, login, promotions):
    login(admin)
    client.post("/cours/nouveau", data={
        "code": "prob201", "title": "Probabilités", "promotion_id": promotions[0].id, "semester": 2,
        "credits": 4, "teacher_id": 0, "description": "",
    })
    assert Course.query.filter_by(code="PROB201").one().semester == 2


def test_deleting_course_removes_files(client, admin, teacher, login, course, app):
    import os

    login(teacher)
    _upload(client, course)
    stored = StoredFile.query.one()
    path = os.path.join(app.config["UPLOAD_FOLDER"], "resource", stored.stored_name)
    client.post("/deconnexion")
    login(admin)
    client.post(f"/cours/{course.id}/supprimer")
    assert not os.path.exists(path)
    assert StoredFile.query.count() == 0
