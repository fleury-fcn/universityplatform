"""Clubs et associations étudiantes."""
from app.extensions import db

from . import TimestampMixin

MEMBER, LEADER = "membre", "responsable"


class Club(TimestampMixin, db.Model):
    __tablename__ = "clubs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.String(30), nullable=False, default="autre")
    description = db.Column(db.Text, nullable=False)
    meeting_frequency = db.Column(db.String(80))
    tags = db.Column(db.String(255))
    contact = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_demo = db.Column(db.Boolean, nullable=False, default=False)

    memberships = db.relationship("ClubMembership", back_populates="club", cascade="all, delete-orphan")
    announcements = db.relationship("ClubAnnouncement", back_populates="club", cascade="all, delete-orphan",
                                    order_by="ClubAnnouncement.created_at.desc()")

    @property
    def tag_list(self):
        return [t.strip() for t in (self.tags or "").split(",") if t.strip()]

    def membership_of(self, user):
        return next((m for m in self.memberships if m.user_id == user.id), None)

    def is_leader(self, user):
        membership = self.membership_of(user)
        return user.is_admin or (membership is not None and membership.role == LEADER)


class ClubMembership(TimestampMixin, db.Model):
    __tablename__ = "club_memberships"
    __table_args__ = (db.UniqueConstraint("club_id", "user_id", name="uq_club_member"),)

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    role = db.Column(db.String(12), nullable=False, default=MEMBER)

    club = db.relationship("Club", back_populates="memberships")
    user = db.relationship("User")


class ClubAnnouncement(TimestampMixin, db.Model):
    __tablename__ = "club_announcements"

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    body = db.Column(db.Text, nullable=False)

    club = db.relationship("Club", back_populates="announcements")
    author = db.relationship("User")
