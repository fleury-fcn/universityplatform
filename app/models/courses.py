"""Cours (unités d'enseignement) et ressources pédagogiques."""
from app.extensions import db

from . import TimestampMixin

RESOURCE_KINDS = ("support", "td", "tp", "examen", "corrige", "autre")


class Course(TimestampMixin, db.Model):
    __tablename__ = "courses"
    __table_args__ = (db.UniqueConstraint("code", "promotion_id", name="uq_course_code_promotion"),)

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    promotion_id = db.Column(db.Integer, db.ForeignKey("promotions.id"), nullable=False, index=True)
    semester = db.Column(db.Integer, nullable=False, default=1)
    credits = db.Column(db.Integer)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    is_demo = db.Column(db.Boolean, nullable=False, default=False)

    promotion = db.relationship("Promotion")
    teacher = db.relationship("User")
    resources = db.relationship("Resource", back_populates="course", cascade="all, delete-orphan",
                                order_by="Resource.created_at.desc()")

    def can_edit(self, user):
        return user.is_admin or (user.is_teacher and self.teacher_id == user.id)

    def visible_to(self, user):
        return user.is_staff or self.promotion_id == user.promotion_id


class Resource(TimestampMixin, db.Model):
    __tablename__ = "resources"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    kind = db.Column(db.String(20), nullable=False, default="support")
    academic_year = db.Column(db.String(9))
    file_id = db.Column(db.Integer, db.ForeignKey("stored_files.id"), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    course = db.relationship("Course", back_populates="resources")
    file = db.relationship("StoredFile")
    uploaded_by = db.relationship("User")
