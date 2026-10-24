from decimal import Decimal

import pytest

from app.grades.routes import parse_grade
from app.models import Grade, Notification
from app.models.grades import semester_results


@pytest.mark.parametrize("raw,expected", [("12,5", Decimal("12.50")), ("0", Decimal("0.00")), ("20", Decimal("20.00")),
                                          ("", None), (" 9.75 ", Decimal("9.75"))])
def test_parse_grade(raw, expected):
    assert parse_grade(raw) == expected


@pytest.mark.parametrize("raw", ["21", "-1", "abc", "1e3"])
def test_parse_grade_rejects(raw):
    with pytest.raises(ValueError):
        parse_grade(raw)


def _enter(client, course, student, value, session="normale", absent=False):
    data = {f"note-{student.id}": value}
    if absent:
        data[f"absent-{student.id}"] = "1"
    return client.post(f"/notes/cours/{course.id}?session={session}", data=data)


def test_only_course_teacher_or_admin_can_enter_grades(client, make_user, login, course):
    student = make_user("etudiant", promotion_id=course.promotion_id)
    login(student)
    assert client.get(f"/notes/cours/{course.id}").status_code == 403
    client.post("/deconnexion")
    login(make_user("enseignant"))
    assert _enter(client, course, student, "20").status_code == 403
    assert Grade.query.count() == 0


def test_grades_hidden_until_published(client, teacher, make_user, login, course):
    student = make_user("etudiant", promotion_id=course.promotion_id)
    login(teacher)
    assert _enter(client, course, student, "15,5").status_code == 302
    client.post("/deconnexion")

    login(student)
    assert "15,50" not in client.get("/notes/").get_data(as_text=True)
    client.post("/deconnexion")

    login(teacher)
    client.post(f"/notes/cours/{course.id}/publier", data={"session": "normale"})
    assert Notification.query.filter_by(user_id=student.id, kind="grades").count() == 1
    client.post("/deconnexion")

    login(student)
    response = client.get("/notes/")
    assert "15,50" in response.get_data(as_text=True)
    assert response.headers["Cache-Control"] == "no-store"


def test_invalid_grade_saves_nothing(client, teacher, make_user, login, course):
    a = make_user("etudiant", promotion_id=course.promotion_id)
    b = make_user("etudiant", promotion_id=course.promotion_id)
    login(teacher)
    response = client.post(f"/notes/cours/{course.id}", data={f"note-{a.id}": "12", f"note-{b.id}": "25"})
    assert response.status_code == 200
    assert Grade.query.count() == 0


def test_student_never_sees_other_students_grades(client, teacher, make_user, login, course):
    a = make_user("etudiant", promotion_id=course.promotion_id)
    b = make_user("etudiant", promotion_id=course.promotion_id)
    login(teacher)
    client.post(f"/notes/cours/{course.id}", data={f"note-{a.id}": "11", f"note-{b.id}": "17,25"})
    client.post(f"/notes/cours/{course.id}/publier", data={"session": "normale"})
    client.post("/deconnexion")
    login(a)
    html = client.get("/notes/").get_data(as_text=True)
    assert "11,00" in html and "17,25" not in html


def test_semester_average_and_retake(app, db, make_user, course, promotions):
    from app.models import Course, utcnow

    other = Course(code="X2", title="Autre", promotion_id=course.promotion_id, semester=1, credits=2)
    course.credits = 4
    db.session.add(other)
    student = make_user("etudiant", promotion_id=course.promotion_id)
    db.session.add_all([
        Grade(student_id=student.id, course_id=course.id, session="normale", value=Decimal("8"), published_at=utcnow()),
        Grade(student_id=student.id, course_id=course.id, session="rattrapage", value=Decimal("12"), published_at=utcnow()),
        Grade(student_id=student.id, course_id=other.id, session="normale", value=Decimal("9"), published_at=utcnow()),
    ])
    db.session.commit()
    (s1,) = semester_results(student, pass_mark=10)
    assert s1["average"] == pytest.approx((12 * 4 + 9 * 2) / 6, abs=0.01)
    assert s1["credits_earned"] == 4
    assert s1["complete"]


def test_absent_counts_as_zero(client, teacher, make_user, login, course):
    student = make_user("etudiant", promotion_id=course.promotion_id)
    login(teacher)
    _enter(client, course, student, "", absent=True)
    client.post(f"/notes/cours/{course.id}/publier", data={"session": "normale"})
    (s1,) = semester_results(student, pass_mark=10)
    assert s1["average"] == 0
    assert s1["rows"][0]["absent"]


def test_csv_export_for_teacher(client, teacher, make_user, login, course):
    student = make_user("etudiant", promotion_id=course.promotion_id, last_name="=HYPERLINK()")
    login(teacher)
    _enter(client, course, student, "13,5")
    response = client.get(f"/notes/cours/{course.id}/export.csv")
    body = response.get_data(as_text=True)
    assert "13,50" in body
    assert "'=HYPERLINK()" in body
