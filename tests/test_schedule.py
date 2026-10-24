from datetime import date, time, timedelta

import pytest

from app.models import Notification, ScheduleEntry
from app.models.schedule import entries_for_day

MONDAY = date(2026, 10, 19)


@pytest.fixture
def weekly(db, promotions):
    p1, _ = promotions
    entry = ScheduleEntry(promotion_id=p1.id, title="Econometrie-Test", kind="CM", weekday=0,
                          start_time=time(8), end_time=time(10))
    db.session.add(entry)
    db.session.commit()
    return entry


def test_recurring_entry_appears_on_its_weekday_only(weekly):
    assert entries_for_day(MONDAY, weekly.promotion_id) == [weekly]
    assert entries_for_day(MONDAY + timedelta(days=1), weekly.promotion_id) == []


def test_validity_period_is_respected(db, weekly):
    weekly.valid_until = MONDAY - timedelta(days=1)
    db.session.commit()
    assert entries_for_day(MONDAY, weekly.promotion_id) == []


def test_cancellation_replaces_the_occurrence(db, weekly):
    change = ScheduleEntry(promotion_id=weekly.promotion_id, title=weekly.title, date=MONDAY,
                           replaces_id=weekly.id, is_cancelled=True, start_time=time(8), end_time=time(10))
    db.session.add(change)
    db.session.commit()
    assert entries_for_day(MONDAY, weekly.promotion_id) == [change]
    assert entries_for_day(MONDAY + timedelta(days=7), weekly.promotion_id) == [weekly]


def test_student_sees_own_promotion_only(client, make_user, login, promotions, weekly):
    p1, p2 = promotions
    login(make_user("etudiant", promotion_id=p2.id))
    html = client.get(f"/emploi-du-temps/?date={MONDAY.isoformat()}&promotion={p1.id}").get_data(as_text=True)
    assert "Econometrie-Test" not in html
    client.post("/deconnexion")
    login(make_user("etudiant", promotion_id=p1.id))
    html = client.get(f"/emploi-du-temps/?date={MONDAY.isoformat()}").get_data(as_text=True)
    assert "Econometrie-Test" in html


def test_week_view(client, make_user, login, promotions, weekly):
    login(make_user("etudiant", promotion_id=promotions[0].id))
    html = client.get(f"/emploi-du-temps/?vue=semaine&date={(MONDAY + timedelta(days=3)).isoformat()}").get_data(as_text=True)
    assert "Econometrie-Test" in html
    assert html.count('class="week-day"') == 6


def test_teacher_sees_own_sessions(client, teacher, login, db, weekly):
    weekly.teacher_id = teacher.id
    db.session.commit()
    login(teacher)
    assert "Econometrie-Test" in client.get(f"/emploi-du-temps/?date={MONDAY.isoformat()}").get_data(as_text=True)


def test_schedule_management_is_admin_only(client, student, teacher, login, weekly):
    for user in (student, teacher):
        login(user)
        assert client.get("/emploi-du-temps/gestion").status_code == 403
        assert client.post(f"/emploi-du-temps/seances/{weekly.id}/supprimer").status_code == 403
        client.post("/deconnexion")


def test_admin_creates_weekly_entry_and_students_are_notified(client, admin, make_user, login, promotions):
    p1, p2 = promotions
    in_p1 = make_user("etudiant", promotion_id=p1.id)
    in_p2 = make_user("etudiant", promotion_id=p2.id)
    login(admin)
    response = client.post("/emploi-du-temps/seances/nouvelle", data={
        "promotion_id": p1.id, "title": "Probabilités", "kind": "TD", "teacher_id": 0, "room_id": 0,
        "repeat": "weekly", "weekday": 2, "start_time": "10:00", "end_time": "12:00", "notify": "y",
    })
    assert response.status_code == 302
    assert ScheduleEntry.query.filter_by(title="Probabilités", weekday=2).one()
    assert Notification.query.filter_by(user_id=in_p1.id).count() == 1
    assert Notification.query.filter_by(user_id=in_p2.id).count() == 0


def test_end_time_must_follow_start(client, admin, login, promotions):
    login(admin)
    response = client.post("/emploi-du-temps/seances/nouvelle", data={
        "promotion_id": promotions[0].id, "title": "X", "kind": "CM", "teacher_id": 0, "room_id": 0,
        "repeat": "weekly", "weekday": 0, "start_time": "10:00", "end_time": "09:00",
    })
    assert "doit être après" in response.get_data(as_text=True)


def test_admin_cancels_one_occurrence(client, admin, make_user, login, weekly):
    student = make_user("etudiant", promotion_id=weekly.promotion_id)
    login(admin)
    response = client.post(f"/emploi-du-temps/seances/{weekly.id}/le/{MONDAY.isoformat()}", data={
        "is_cancelled": "y", "start_time": "08:00", "end_time": "10:00", "room_id": 0, "notify": "y",
    })
    assert response.status_code == 302
    entries = entries_for_day(MONDAY, weekly.promotion_id)
    assert len(entries) == 1 and entries[0].is_cancelled
    notification = Notification.query.filter_by(user_id=student.id).one()
    assert "annulée" in notification.title

    client.post(f"/emploi-du-temps/seances/{weekly.id}/le/{MONDAY.isoformat()}/retablir")
    assert entries_for_day(MONDAY, weekly.promotion_id) == [weekly]


def test_occurrence_on_wrong_weekday_is_404(client, admin, login, weekly):
    login(admin)
    tuesday = (MONDAY + timedelta(days=1)).isoformat()
    assert client.get(f"/emploi-du-temps/seances/{weekly.id}/le/{tuesday}").status_code == 404
