from itertools import groupby

from flask import abort, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required
from sqlalchemy import or_

from app.core.files import UploadError, access_rule, accept_attribute, category_rules, delete_stored, save_upload
from app.core.security import ROLE_TEACHER, admin_required
from app.extensions import db
from app.models import Promotion, User
from app.models.courses import Course, Resource
from app.services.notifications import notify, recipients

from . import bp
from .forms import KIND_LABELS, CourseForm, ResourceForm


@access_rule("resource")
def _can_download_resource(user, stored):
    resource = Resource.query.filter_by(file_id=stored.id).first()
    return resource is not None and resource.course.visible_to(user)


def _visible_courses():
    query = Course.query
    if current_user.is_student:
        query = query.filter(Course.promotion_id == current_user.promotion_id)
    return query


@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    promotion_id = request.args.get("promotion", type=int)
    mine = request.args.get("mes") == "1"
    query = _visible_courses()
    promotions = []
    if current_user.is_staff:
        promotions = Promotion.query.filter_by(is_active=True).order_by(Promotion.name).all()
        if mine:
            query = query.filter(Course.teacher_id == current_user.id)
        elif promotion_id:
            query = query.filter(Course.promotion_id == promotion_id)
        elif current_user.is_teacher:
            mine = True
            query = query.filter(Course.teacher_id == current_user.id)
    if q:
        query = query.filter(or_(Course.title.ilike(f"%{q}%"), Course.code.ilike(f"%{q}%")))
    courses = query.order_by(Course.semester, Course.title).all()
    by_semester = [(sem, list(items)) for sem, items in groupby(courses, key=lambda c: c.semester)]
    return render_template("courses/index.html", by_semester=by_semester, q=q, promotions=promotions,
                           promotion_id=promotion_id, mine=mine)


@bp.route("/<int:course_id>", methods=["GET", "POST"])
@login_required
def show(course_id):
    course = db.get_or_404(Course, course_id)
    if not course.visible_to(current_user):
        abort(404)
    form = ResourceForm() if course.can_edit(current_user) else None
    if form and form.validate_on_submit():
        try:
            stored = save_upload(form.file.data, "resource", current_user.id)
        except UploadError as err:
            form.file.errors.append(str(err))
        else:
            db.session.flush()
            resource = Resource(course=course, title=form.title.data, kind=form.kind.data,
                                academic_year=form.academic_year.data, file=stored,
                                uploaded_by_id=current_user.id)
            db.session.add(resource)
            notify(recipients(course.promotion_id, include_staff=False), "resource",
                   _("Nouveau document en %(course)s : %(title)s", course=course.title, title=resource.title),
                   url=url_for("courses.show", course_id=course.id), exclude=current_user.id)
            db.session.commit()
            flash(_("Document ajouté."), "success")
            return redirect(url_for("courses.show", course_id=course.id))
    grouped = [(kind, [r for r in course.resources if r.kind == kind]) for kind in KIND_LABELS]
    max_bytes = category_rules("resource")[1]
    return render_template("courses/show.html", course=course, grouped=[g for g in grouped if g[1]],
                           kind_labels=KIND_LABELS, form=form, accept=accept_attribute("resource"),
                           max_bytes=max_bytes)


@bp.route("/ressources/<int:resource_id>/supprimer", methods=["POST"])
@login_required
def delete_resource(resource_id):
    resource = db.get_or_404(Resource, resource_id)
    course = resource.course
    if not course.can_edit(current_user):
        abort(403)
    stored = resource.file
    db.session.delete(resource)
    delete_stored(stored)
    db.session.commit()
    flash(_("Document supprimé."), "success")
    return redirect(url_for("courses.show", course_id=course.id))


# --- Gestion des cours (administration) ------------------------------------

@bp.route("/gestion")
@admin_required
def manage():
    promotion_id = request.args.get("promotion", type=int)
    promotions = Promotion.query.order_by(Promotion.name).all()
    query = Course.query
    if promotion_id:
        query = query.filter_by(promotion_id=promotion_id)
    courses = query.order_by(Course.promotion_id, Course.semester, Course.title).all()
    return render_template("courses/manage.html", courses=courses, promotions=promotions, promotion_id=promotion_id)


@bp.route("/nouveau", methods=["GET", "POST"], defaults={"course_id": None})
@bp.route("/<int:course_id>/modifier", methods=["GET", "POST"])
@admin_required
def edit(course_id):
    course = db.get_or_404(Course, course_id) if course_id else None
    form = CourseForm(obj=course)
    form.promotion_id.choices = [(p.id, p.name) for p in Promotion.query.order_by(Promotion.name)]
    form.teacher_id.choices = [(0, "—")] + [
        (u.id, u.full_name) for u in User.query.filter_by(role=ROLE_TEACHER, is_active=True).order_by(User.last_name)
    ]
    if request.method == "GET":
        form.teacher_id.data = course.teacher_id if course and course.teacher_id else 0
        if not course:
            form.promotion_id.data = request.args.get("promotion", type=int)
    if form.validate_on_submit():
        duplicate = Course.query.filter_by(code=form.code.data, promotion_id=form.promotion_id.data)
        if course:
            duplicate = duplicate.filter(Course.id != course.id)
        if duplicate.first():
            form.code.errors.append(_("Ce code existe déjà pour cette promotion."))
        else:
            if course is None:
                course = Course()
                db.session.add(course)
            form.populate_obj(course)
            course.teacher_id = form.teacher_id.data or None
            db.session.commit()
            flash(_("Cours enregistré."), "success")
            return redirect(url_for("courses.manage", promotion=course.promotion_id))
    return render_template("courses/edit.html", form=form, course=course)


@bp.route("/<int:course_id>/supprimer", methods=["POST"])
@admin_required
def delete(course_id):
    course = db.get_or_404(Course, course_id)
    promotion_id = course.promotion_id
    files = [resource.file for resource in course.resources]
    db.session.delete(course)  # supprime aussi ressources et notes (cascade)
    for stored in files:
        delete_stored(stored)
    db.session.commit()
    flash(_("Cours supprimé."), "success")
    return redirect(url_for("courses.manage", promotion=promotion_id))
