import io
from datetime import time

from app.core.dates import local_today
from app.models import CampusMap, Room, ScheduleEntry

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def test_campus_list_search_and_detail(client, student, login, db):
    db.session.add_all([Room(code="A1", name="Amphi A", kind="amphi", capacity=120),
                        Room(code="L1", name="Labo info", kind="labo")])
    db.session.commit()
    login(student)
    html = client.get("/campus/?q=labo").get_data(as_text=True)
    assert "Labo info" in html and "Amphi A" not in html
    html = client.get("/campus/?type=amphi").get_data(as_text=True)
    assert "Amphi A" in html and "Labo info" not in html
    room = Room.query.filter_by(code="A1").one()
    assert "120 places" in client.get(f"/campus/salles/{room.id}").get_data(as_text=True)


def test_room_shows_todays_sessions(client, student, login, db, promotions):
    room = Room(code="S2", name="Salle 2")
    db.session.add(room)
    db.session.flush()
    db.session.add(ScheduleEntry(promotion_id=promotions[0].id, title="Cours-Dans-S2", weekday=local_today().weekday(),
                                 start_time=time(8), end_time=time(9), room_id=room.id))
    db.session.commit()
    login(student)
    assert "Cours-Dans-S2" in client.get(f"/campus/salles/{room.id}").get_data(as_text=True)


def test_map_link_only_with_coordinates(client, student, login, db):
    with_gps = Room(code="G1", name="Avec GPS", latitude=-3.38, longitude=29.36)
    without = Room(code="G2", name="Sans GPS")
    db.session.add_all([with_gps, without])
    db.session.commit()
    login(student)
    assert "geo:-3.38,29.36" in client.get(f"/campus/salles/{with_gps.id}").get_data(as_text=True)
    assert "geo:" not in client.get(f"/campus/salles/{without.id}").get_data(as_text=True)


def test_campus_management_admin_only(client, student, teacher, login):
    for user in (student, teacher):
        login(user)
        assert client.get("/campus/gestion").status_code == 403
        assert client.post("/campus/gestion/salles/nouvelle", data={"code": "X", "name": "X"}).status_code == 403
        client.post("/deconnexion")


def test_admin_creates_room_and_uploads_map(client, admin, student, login):
    login(admin)
    client.post("/campus/gestion/salles/nouvelle", data={"code": "b12", "name": "Salle B12", "kind": "salle"})
    assert Room.query.filter_by(code="B12").one()
    response = client.post("/campus/gestion", data={"title": "Plan général", "image": (io.BytesIO(PNG), "plan.png")},
                           content_type="multipart/form-data")
    assert response.status_code == 302
    campus_map = CampusMap.query.one()
    client.post("/deconnexion")
    login(student)
    assert "Plan général" in client.get("/campus/").get_data(as_text=True)
    assert client.get(f"/fichiers/{campus_map.file.id}/plan.png").status_code == 200


def test_partial_coordinates_rejected(client, admin, login):
    login(admin)
    response = client.post("/campus/gestion/salles/nouvelle", data={"code": "C1", "name": "C", "kind": "salle",
                                                                   "latitude": "-3.4"})
    assert "latitude et la longitude" in response.get_data(as_text=True)
    assert Room.query.count() == 0
