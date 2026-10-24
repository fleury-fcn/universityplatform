import pytest

from app.models import Club, ClubAnnouncement, ClubMembership, Notification


@pytest.fixture
def club(db):
    c = Club(name="Club Test", category="science", description="Description")
    db.session.add(c)
    db.session.commit()
    return c


def test_join_and_leave(client, student, login, club):
    login(student)
    client.post(f"/clubs/{club.id}/rejoindre")
    client.post(f"/clubs/{club.id}/rejoindre")
    assert ClubMembership.query.filter_by(user_id=student.id).count() == 1
    client.post(f"/clubs/{club.id}/quitter")
    assert ClubMembership.query.count() == 0


def test_member_list_visible_to_leaders_only(client, make_user, login, club, db):
    a = make_user("etudiant", first_name="Visible", last_name="Membre")
    db.session.add(ClubMembership(club_id=club.id, user_id=a.id))
    db.session.commit()
    login(make_user("etudiant"))
    assert "Visible Membre" not in client.get(f"/clubs/{club.id}").get_data(as_text=True)


def test_leader_announcement_notifies_members(client, make_user, login, club, db):
    leader, member = make_user("etudiant"), make_user("etudiant")
    db.session.add_all([ClubMembership(club_id=club.id, user_id=leader.id, role="responsable"),
                        ClubMembership(club_id=club.id, user_id=member.id)])
    db.session.commit()
    login(leader)
    client.post(f"/clubs/{club.id}", data={"body": "Réunion jeudi"})
    assert ClubAnnouncement.query.count() == 1
    assert Notification.query.filter_by(user_id=member.id, kind="club").count() == 1
    assert Notification.query.filter_by(user_id=leader.id).count() == 0


def test_simple_member_cannot_announce(client, student, login, club, db):
    db.session.add(ClubMembership(club_id=club.id, user_id=student.id))
    db.session.commit()
    login(student)
    client.post(f"/clubs/{club.id}", data={"body": "Spam"})
    assert ClubAnnouncement.query.count() == 0


def test_admin_appoints_leader(client, admin, student, login, club):
    login(admin)
    client.post(f"/clubs/{club.id}/responsables", data={"identifier": student.matricule})
    membership = ClubMembership.query.filter_by(user_id=student.id).one()
    assert membership.role == "responsable"


def test_club_management_admin_only(client, student, login, club):
    login(student)
    assert client.get("/clubs/gestion").status_code == 403
    assert client.post(f"/clubs/{club.id}/responsables", data={"identifier": student.matricule}).status_code == 403


def test_inactive_club_hidden(client, student, login, club, db):
    club.is_active = False
    db.session.commit()
    login(student)
    assert "Club Test" not in client.get("/clubs/").get_data(as_text=True)
    assert client.get(f"/clubs/{club.id}").status_code == 404
