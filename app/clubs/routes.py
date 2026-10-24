from flask import abort, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required
from flask_wtf import FlaskForm

from app.core.security import admin_required
from app.extensions import db
from app.models import Club, ClubAnnouncement, ClubMembership, User
from app.models.clubs import LEADER, MEMBER
from app.services.notifications import notify

from . import bp
from .forms import CATEGORY_LABELS, AnnouncementForm, ClubForm, LeaderForm


@bp.route("/")
@login_required
def index():
    category = request.args.get("categorie", "")
    query = Club.query.filter_by(is_active=True)
    if category in CATEGORY_LABELS:
        query = query.filter_by(category=category)
    clubs = query.order_by(Club.name).all()
    my_clubs = {m.club_id for m in ClubMembership.query.filter_by(user_id=current_user.id)}
    return render_template("clubs/index.html", clubs=clubs, categories=CATEGORY_LABELS, category=category,
                           my_clubs=my_clubs)


@bp.route("/<int:club_id>", methods=["GET", "POST"])
@login_required
def show(club_id):
    club = db.get_or_404(Club, club_id)
    if not club.is_active and not current_user.is_admin:
        abort(404)
    is_leader = club.is_leader(current_user)
    form = AnnouncementForm() if is_leader else None
    if form and form.validate_on_submit():
        db.session.add(ClubAnnouncement(club=club, author_id=current_user.id, body=form.body.data.strip()))
        notify([m.user_id for m in club.memberships], "club", _("%(club)s : nouvelle annonce", club=club.name),
               url=url_for("clubs.show", club_id=club.id), exclude=current_user.id)
        db.session.commit()
        flash(_("Annonce publiée et envoyée aux membres."), "success")
        return redirect(url_for("clubs.show", club_id=club.id))
    members = sorted(club.memberships, key=lambda m: (m.role != LEADER, m.user.last_name))
    return render_template("clubs/show.html", club=club, membership=club.membership_of(current_user),
                           is_leader=is_leader, form=form, members=members, categories=CATEGORY_LABELS,
                           csrf_form=FlaskForm(), leader_form=LeaderForm() if current_user.is_admin else None)


@bp.route("/<int:club_id>/rejoindre", methods=["POST"])
@login_required
def join(club_id):
    club = db.get_or_404(Club, club_id)
    if not FlaskForm().validate_on_submit() or not club.is_active:
        abort(400)
    if club.membership_of(current_user) is None:
        db.session.add(ClubMembership(club=club, user_id=current_user.id, role=MEMBER))
        db.session.commit()
        flash(_("Bienvenue au club %(club)s !", club=club.name), "success")
    return redirect(url_for("clubs.show", club_id=club.id))


@bp.route("/<int:club_id>/quitter", methods=["POST"])
@login_required
def leave(club_id):
    club = db.get_or_404(Club, club_id)
    if not FlaskForm().validate_on_submit():
        abort(400)
    membership = club.membership_of(current_user)
    if membership:
        db.session.delete(membership)
        db.session.commit()
        flash(_("Vous avez quitté le club."), "info")
    return redirect(url_for("clubs.show", club_id=club.id))


@bp.route("/annonces/<int:announcement_id>/supprimer", methods=["POST"])
@login_required
def delete_announcement(announcement_id):
    announcement = db.get_or_404(ClubAnnouncement, announcement_id)
    if not announcement.club.is_leader(current_user) or not FlaskForm().validate_on_submit():
        abort(403)
    club_id = announcement.club_id
    db.session.delete(announcement)
    db.session.commit()
    return redirect(url_for("clubs.show", club_id=club_id))


# --- Gestion (administration) ---------------------------------------------

@bp.route("/gestion")
@admin_required
def manage():
    clubs = Club.query.order_by(Club.name).all()
    return render_template("clubs/manage.html", clubs=clubs, categories=CATEGORY_LABELS)


@bp.route("/nouveau", methods=["GET", "POST"], defaults={"club_id": None})
@bp.route("/<int:club_id>/modifier", methods=["GET", "POST"])
@admin_required
def edit(club_id):
    club = db.get_or_404(Club, club_id) if club_id else None
    form = ClubForm(obj=club)
    if form.validate_on_submit():
        duplicate = Club.query.filter(Club.name == form.name.data)
        if club:
            duplicate = duplicate.filter(Club.id != club.id)
        if duplicate.first():
            form.name.errors.append(_("Un club porte déjà ce nom."))
        else:
            if club is None:
                club = Club()
                db.session.add(club)
            form.populate_obj(club)
            db.session.commit()
            flash(_("Club enregistré."), "success")
            return redirect(url_for("clubs.show", club_id=club.id))
    return render_template("clubs/edit.html", form=form, club=club)


@bp.route("/<int:club_id>/responsables", methods=["POST"])
@admin_required
def set_leader(club_id):
    club = db.get_or_404(Club, club_id)
    form = LeaderForm()
    if form.validate_on_submit():
        user = User.find_by_login(form.identifier.data)
        if user is None:
            flash(_("Aucun compte ne correspond à cet identifiant."), "danger")
        else:
            membership = club.membership_of(user)
            if membership is None:
                membership = ClubMembership(club=club, user_id=user.id)
                db.session.add(membership)
            membership.role = LEADER
            db.session.commit()
            flash(_("%(name)s est responsable du club.", name=user.full_name), "success")
    return redirect(url_for("clubs.show", club_id=club.id))


@bp.route("/membres/<int:membership_id>/role", methods=["POST"])
@admin_required
def toggle_role(membership_id):
    membership = db.get_or_404(ClubMembership, membership_id)
    if not FlaskForm().validate_on_submit():
        abort(400)
    membership.role = MEMBER if membership.role == LEADER else LEADER
    db.session.commit()
    return redirect(url_for("clubs.show", club_id=membership.club_id))
