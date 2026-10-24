import csv
import io
from decimal import Decimal, InvalidOperation

from flask import Response, abort, current_app, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required
from flask_wtf import FlaskForm

from app.core.security import ROLE_STUDENT, no_store
from app.extensions import db
from app.models import Course, Promotion, User, utcnow
from app.models.grades import SESSIONS, Grade, semester_results
from app.services.notifications import notify
from app.services.users import csv_safe

from . import bp


def parse_grade(raw):
    """« 12,5 » ou « 12.5 » -> Decimal entre 0 et 20 ; chaîne vide -> None. Lève ValueError sinon."""
    raw = (raw or "").strip().replace(",", ".")
    if not raw:
        return None
    try:
        value = Decimal(raw).quantize(Decimal("0.01"))
    except InvalidOperation:
        raise ValueError(raw)
    if not Decimal(0) <= value <= Decimal(20):
        raise ValueError(raw)
    return value


@bp.route("/")
@login_required
@no_store
def index():
    if current_user.is_student:
        results = semester_results(current_user, current_app.config["PASS_MARK"]) if current_user.promotion_id else []
        return render_template("grades/student.html", results=results, pass_mark=current_app.config["PASS_MARK"])
    query = Course.query
    promotion_id = request.args.get("promotion", type=int)
    promotions = []
    if current_user.is_teacher:
        query = query.filter_by(teacher_id=current_user.id)
    else:
        promotions = Promotion.query.filter_by(is_active=True).order_by(Promotion.name).all()
        if promotion_id:
            query = query.filter_by(promotion_id=promotion_id)
    courses = query.order_by(Course.promotion_id, Course.semester, Course.title).all()
    return render_template("grades/staff.html", courses=courses, promotions=promotions, promotion_id=promotion_id)


def _course_for_editing(course_id):
    course = db.get_or_404(Course, course_id)
    if not course.can_edit(current_user):
        abort(403)
    return course


def _students(course):
    return (User.query.filter_by(promotion_id=course.promotion_id, role=ROLE_STUDENT, is_active=True)
            .order_by(User.last_name, User.first_name).all())


@bp.route("/cours/<int:course_id>", methods=["GET", "POST"])
@login_required
@no_store
def sheet(course_id):
    course = _course_for_editing(course_id)
    session = request.args.get("session", "normale")
    if session not in SESSIONS:
        abort(404)
    students = _students(course)
    existing = {g.student_id: g for g in Grade.query.filter_by(course_id=course.id, session=session)}
    form = FlaskForm()  # protection CSRF
    errors = {}
    if form.validate_on_submit():
        parsed = {}
        for student in students:
            absent = request.form.get(f"absent-{student.id}") == "1"
            try:
                parsed[student.id] = (None if absent else parse_grade(request.form.get(f"note-{student.id}")), absent)
            except ValueError:
                errors[student.id] = request.form.get(f"note-{student.id}")
        if errors:
            flash(_("Certaines notes sont invalides (nombre entre 0 et 20 attendu). Rien n'a été enregistré."), "danger")
        else:
            for student in students:
                value, absent = parsed[student.id]
                grade = existing.get(student.id)
                if value is None and not absent:
                    if grade and grade.published_at is None:
                        db.session.delete(grade)
                    continue
                if grade is None:
                    grade = Grade(student_id=student.id, course_id=course.id, session=session)
                    db.session.add(grade)
                    existing[student.id] = grade
                grade.value, grade.is_absent, grade.entered_by_id = value, absent, current_user.id
            db.session.commit()
            flash(_("Notes enregistrées."), "success")
            return redirect(url_for("grades.sheet", course_id=course.id, session=session))
    published = any(g.published_at for g in existing.values())
    pending = sum(1 for g in existing.values() if g.published_at is None)
    return render_template("grades/sheet.html", course=course, session=session, students=students,
                           grades=existing, errors=errors, form=form, published=published, pending=pending,
                           sessions=SESSIONS)


@bp.route("/cours/<int:course_id>/publier", methods=["POST"])
@login_required
def publish(course_id):
    course = _course_for_editing(course_id)
    session = request.form.get("session", "normale")
    if session not in SESSIONS or not FlaskForm().validate_on_submit():
        abort(400)
    grades = Grade.query.filter_by(course_id=course.id, session=session, published_at=None).all()
    now = utcnow()
    for grade in grades:
        grade.published_at = now
    notify([g.student_id for g in grades], "grades",
           _("Note publiée : %(course)s (session %(session)s)", course=course.title, session=session),
           url=url_for("grades.index"))
    db.session.commit()
    flash(_("%(n)d note(s) publiée(s). Les étudiants ont été prévenus.", n=len(grades)), "success")
    return redirect(url_for("grades.sheet", course_id=course.id, session=session))


@bp.route("/cours/<int:course_id>/export.csv")
@login_required
def export(course_id):
    course = _course_for_editing(course_id)
    session = request.args.get("session", "normale")
    grades = {g.student_id: g for g in Grade.query.filter_by(course_id=course.id, session=session)}
    out = io.StringIO()
    writer = csv.writer(out, delimiter=";")
    writer.writerow(["matricule", "nom", "prenom", "note", "absent", "publiee"])
    for student in _students(course):
        g = grades.get(student.id)
        writer.writerow([
            csv_safe(student.matricule or ""), csv_safe(student.last_name), csv_safe(student.first_name),
            "" if not g or g.value is None else str(g.value).replace(".", ","),
            "oui" if g and g.is_absent else "", "oui" if g and g.published_at else "",
        ])
    filename = f"notes_{course.code}_{session}.csv"
    return Response("﻿" + out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={filename}", "Cache-Control": "no-store"})
