"""Notes par cours et par session."""
from app.extensions import db

from . import TimestampMixin, utcnow

SESSIONS = ("normale", "rattrapage")


class Grade(TimestampMixin, db.Model):
    __tablename__ = "grades"
    __table_args__ = (db.UniqueConstraint("student_id", "course_id", "session", name="uq_grade"),)

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    session = db.Column(db.String(12), nullable=False, default="normale")
    value = db.Column(db.Numeric(4, 2))
    is_absent = db.Column(db.Boolean, nullable=False, default=False)
    published_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    entered_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    student = db.relationship("User", foreign_keys=[student_id])
    course = db.relationship("Course", backref=db.backref("grades", cascade="all, delete-orphan"))


def semester_results(student, pass_mark):
    """Résultats publiés d'un étudiant, regroupés par semestre.

    La note de rattrapage, si elle existe, remplace celle de la session normale.
    Moyenne pondérée par les crédits (1 si non renseignés). Calcul indicatif.
    """
    from .courses import Course

    courses = Course.query.filter_by(promotion_id=student.promotion_id).order_by(Course.semester, Course.title).all()
    grades = Grade.query.filter(Grade.student_id == student.id, Grade.published_at.isnot(None)).all()
    by_course = {}
    for g in grades:
        by_course.setdefault(g.course_id, {})[g.session] = g

    semesters = {}
    for course in courses:
        sessions = by_course.get(course.id, {})
        final = sessions.get("rattrapage") or sessions.get("normale")
        value = None if final is None or final.is_absent or final.value is None else float(final.value)
        row = {
            "course": course,
            "normale": sessions.get("normale"),
            "rattrapage": sessions.get("rattrapage"),
            "value": value,
            "absent": bool(final and final.is_absent),
            "validated": value is not None and value >= pass_mark,
        }
        semesters.setdefault(course.semester, []).append(row)

    results = []
    for semester, rows in sorted(semesters.items()):
        graded = [r for r in rows if r["value"] is not None or r["absent"]]
        weights = sum((r["course"].credits or 1) for r in graded)
        total = sum((r["value"] or 0) * (r["course"].credits or 1) for r in graded)
        results.append({
            "semester": semester,
            "rows": rows,
            "average": round(total / weights, 2) if weights else None,
            "credits_earned": sum((r["course"].credits or 0) for r in rows if r["validated"]),
            "credits_total": sum((r["course"].credits or 0) for r in rows),
            "complete": len(graded) == len(rows),
        })
    return results
