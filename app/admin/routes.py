from flask import Response, abort, current_app, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from sqlalchemy import func, or_

from app.core.security import ROLE_STUDENT, admin_required, no_store
from app.extensions import db
from app.models import Promotion, User
from app.services.users import (
    create_user,
    credentials_csv,
    find_conflict,
    generate_temp_password,
    import_users_csv,
    normalize_identity,
)

from . import bp
from .forms import ImportUsersForm, UserForm

# Rubriques de l'administration, affichées si la vue correspondante existe.
SECTIONS = [
    {"endpoint": "admin.users", "label": _l("Utilisateurs"), "icon": "users"},
    {"endpoint": "admin.academic", "label": _l("Filières et promotions"), "icon": "settings"},
    {"endpoint": "news.manage", "label": _l("Actualités"), "icon": "news"},
    {"endpoint": "schedule.manage", "label": _l("Emploi du temps"), "icon": "calendar"},
    {"endpoint": "courses.manage", "label": _l("Cours"), "icon": "book"},
    {"endpoint": "library.manage", "label": _l("Bibliothèque"), "icon": "library"},
    {"endpoint": "campus.manage", "label": _l("Campus et salles"), "icon": "map"},
    {"endpoint": "clubs.manage", "label": _l("Clubs"), "icon": "users"},
    {"endpoint": "tips.moderate", "label": _l("Modération des tuyaux"), "icon": "bulb"},
    {"endpoint": "faq.manage", "label": _l("Questions fréquentes"), "icon": "help"},
]

PER_PAGE = 25


@bp.route("/")
@admin_required
def index():
    counts = dict(db.session.query(User.role, func.count()).filter(User.is_active.is_(True)).group_by(User.role).all())
    pending = User.query.filter_by(is_active=False, last_login_at=None).count()
    demo_users = User.query.filter_by(is_demo=True, is_active=True).count()
    sections = [s for s in SECTIONS if s["endpoint"] in current_app.view_functions]
    return render_template("admin/index.html", counts=counts, pending=pending, demo_users=demo_users, sections=sections)


@bp.route("/utilisateurs")
@admin_required
def users():
    q = request.args.get("q", "").strip()
    role = request.args.get("role", "")
    status = request.args.get("statut", "")
    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.first_name.ilike(like), User.last_name.ilike(like), User.username.ilike(like),
                                 User.matricule.ilike(like), User.email.ilike(like)))
    if role:
        query = query.filter(User.role == role)
    if status == "actifs":
        query = query.filter(User.is_active.is_(True))
    elif status == "inactifs":
        query = query.filter(User.is_active.is_(False))
    page = query.order_by(User.last_name, User.first_name).paginate(per_page=PER_PAGE, error_out=False)
    return render_template("admin/users.html", page=page, q=q, role=role, status=status)


def _populate_form_choices(form):
    form.promotion_id.choices = [(0, "—")] + [
        (p.id, f"{p.name} ({p.academic_year})") for p in Promotion.query.order_by(Promotion.name)
    ]


@bp.route("/utilisateurs/nouveau", methods=["GET", "POST"])
@admin_required
@no_store
def user_new():
    form = UserForm()
    _populate_form_choices(form)
    if form.validate_on_submit():
        username, matricule, email = normalize_identity(form.username.data, form.matricule.data, form.email.data)
        conflict = find_conflict(username, matricule, email)
        if conflict:
            flash(conflict, "danger")
        else:
            user, password = create_user(
                first_name=form.first_name.data, last_name=form.last_name.data, role=form.role.data,
                username=username, matricule=matricule, email=email,
                promotion_id=form.promotion_id.data or None, is_active=form.is_active.data,
            )
            db.session.commit()
            return render_template("admin/password_issued.html", user=user, password=password, created=True)
    return render_template("admin/user_form.html", form=form, user=None)


@bp.route("/utilisateurs/<int:user_id>", methods=["GET", "POST"])
@admin_required
@no_store
def user_edit(user_id):
    user = db.get_or_404(User, user_id)
    form = UserForm(obj=user)
    _populate_form_choices(form)
    if request.method == "GET":
        form.promotion_id.data = user.promotion_id or 0
    if form.validate_on_submit():
        username, matricule, email = normalize_identity(form.username.data, form.matricule.data, form.email.data)
        conflict = find_conflict(username, matricule, email, exclude_id=user.id)
        if conflict:
            flash(conflict, "danger")
        elif user.id == current_user.id and (form.role.data != user.role or not form.is_active.data):
            flash(_("Vous ne pouvez pas retirer vos propres droits d'administration."), "danger")
        else:
            user.username, user.matricule, user.email = username, matricule, email
            user.first_name, user.last_name = form.first_name.data, form.last_name.data
            user.role = form.role.data
            user.promotion_id = (form.promotion_id.data or None) if user.role == ROLE_STUDENT else None
            if user.is_active and not form.is_active.data:
                user.session_version += 1  # déconnecte le compte partout
            user.is_active = form.is_active.data
            db.session.commit()
            flash(_("Compte mis à jour."), "success")
            return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, user=user)


@bp.route("/utilisateurs/<int:user_id>/mot-de-passe", methods=["POST"])
@admin_required
@no_store
def user_reset_password(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        abort(400)
    password = generate_temp_password()
    user.set_password(password)
    user.must_change_password = True
    user.failed_logins, user.locked_until = 0, None
    db.session.commit()
    return render_template("admin/password_issued.html", user=user, password=password, created=False)


@bp.route("/utilisateurs/<int:user_id>/activer", methods=["POST"])
@admin_required
def user_activate(user_id):
    user = db.get_or_404(User, user_id)
    user.is_active = True
    db.session.commit()
    flash(_("Compte de %(name)s activé.", name=user.full_name), "success")
    return redirect(url_for("admin.users", statut="inactifs"))


@bp.route("/utilisateurs/import", methods=["GET", "POST"])
@admin_required
@no_store
def users_import():
    form = ImportUsersForm()
    errors = []
    if form.validate_on_submit():
        raw = form.file.data.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            errors = [_("Fichier trop volumineux (1 Mo maximum).")]
        else:
            created, errors = import_users_csv(raw)
            if created:
                return Response(
                    credentials_csv(created),
                    mimetype="text/csv",
                    headers={
                        "Content-Disposition": "attachment; filename=comptes_crees.csv",
                        "Cache-Control": "no-store",
                    },
                )
            if not errors:
                errors = [_("Aucune ligne à importer.")]
    return render_template("admin/users_import.html", form=form, errors=errors)
