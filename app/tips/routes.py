from flask import abort, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from sqlalchemy import func

from app.core.files import UploadError, access_rule, accept_attribute, category_rules, delete_stored, save_upload
from app.core.security import ROLE_ADMIN, admin_required
from app.extensions import db
from app.models import Course, Tip, TipReport, TipVote, User, utcnow
from app.models.tips import PENDING, PUBLISHED, REJECTED
from app.services.notifications import notify

from . import bp
from .forms import CATEGORY_LABELS, ModerationForm, ReportForm, TipForm

PER_PAGE = 20


@access_rule("tip")
def _can_download_tip_file(user, stored):
    tip = Tip.query.filter_by(file_id=stored.id).first()
    return tip is not None and tip.visible_to(user)


def _admin_ids():
    return [uid for (uid,) in db.session.query(User.id).filter_by(role=ROLE_ADMIN, is_active=True)]


@bp.route("/")
@login_required
def index():
    category = request.args.get("categorie", "")
    order = request.args.get("tri", "recents")
    votes = (db.session.query(TipVote.tip_id, func.count().label("n")).group_by(TipVote.tip_id).subquery())
    query = (db.session.query(Tip, func.coalesce(votes.c.n, 0))
             .outerjoin(votes, votes.c.tip_id == Tip.id).filter(Tip.status == PUBLISHED))
    if category in CATEGORY_LABELS:
        query = query.filter(Tip.category == category)
    if order == "utiles":
        query = query.order_by(func.coalesce(votes.c.n, 0).desc(), Tip.published_at.desc())
    else:
        query = query.order_by(Tip.published_at.desc())
    page = query.paginate(per_page=PER_PAGE, error_out=False)
    mine_pending = Tip.query.filter(Tip.author_id == current_user.id, Tip.status != PUBLISHED).count()
    return render_template("tips/index.html", page=page, categories=CATEGORY_LABELS, category=category,
                           order=order, mine_pending=mine_pending)


@bp.route("/<int:tip_id>")
@login_required
def show(tip_id):
    tip = db.get_or_404(Tip, tip_id)
    if not tip.visible_to(current_user):
        abort(404)
    voted = TipVote.query.filter_by(tip_id=tip.id, user_id=current_user.id).first() is not None
    return render_template("tips/show.html", tip=tip, categories=CATEGORY_LABELS, voted=voted,
                           votes=len(tip.votes), csrf_form=FlaskForm(), report_form=ReportForm(),
                           moderation_form=ModerationForm() if current_user.is_admin else None)


@bp.route("/mes-tuyaux")
@login_required
def mine():
    tips = Tip.query.filter_by(author_id=current_user.id).order_by(Tip.created_at.desc()).all()
    return render_template("tips/mine.html", tips=tips, categories=CATEGORY_LABELS)


@bp.route("/nouveau", methods=["GET", "POST"])
@login_required
def new():
    form = TipForm()
    courses = Course.query.order_by(Course.title)
    if current_user.is_student:
        courses = courses.filter_by(promotion_id=current_user.promotion_id)
    form.course_id.choices = [(0, "—")] + [(c.id, c.title) for c in courses]
    if form.validate_on_submit():
        stored = None
        if form.attachment.data:
            try:
                stored = save_upload(form.attachment.data, "tip", current_user.id)
            except UploadError as err:
                form.attachment.errors.append(str(err))
        if not form.attachment.errors:
            auto_publish = current_user.is_staff
            tip = Tip(title=form.title.data, body=form.body.data.strip(), category=form.category.data,
                      course_id=form.course_id.data or None, author_id=current_user.id, file=stored,
                      status=PUBLISHED if auto_publish else PENDING,
                      published_at=utcnow() if auto_publish else None)
            db.session.add(tip)
            db.session.flush()
            if auto_publish:
                flash(_("Tuyau publié."), "success")
            else:
                notify(_admin_ids(), "moderation", _("Tuyau à modérer : %(t)s", t=tip.title),
                       url=url_for("tips.show", tip_id=tip.id))
                flash(_("Merci ! Votre tuyau sera visible après validation par l'administration."), "success")
            db.session.commit()
            return redirect(url_for("tips.show", tip_id=tip.id))
    max_bytes = category_rules("tip")[1]
    return render_template("tips/new.html", form=form, accept=accept_attribute("tip"), max_bytes=max_bytes)


@bp.route("/<int:tip_id>/utile", methods=["POST"])
@login_required
def vote(tip_id):
    tip = db.get_or_404(Tip, tip_id)
    if tip.status != PUBLISHED or not FlaskForm().validate_on_submit():
        abort(400)
    existing = TipVote.query.filter_by(tip_id=tip.id, user_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
    elif tip.author_id != current_user.id:
        db.session.add(TipVote(tip_id=tip.id, user_id=current_user.id))
    db.session.commit()
    return redirect(url_for("tips.show", tip_id=tip.id))


@bp.route("/<int:tip_id>/signaler", methods=["POST"])
@login_required
def report(tip_id):
    tip = db.get_or_404(Tip, tip_id)
    form = ReportForm()
    if tip.status != PUBLISHED or not form.validate_on_submit():
        abort(400)
    if not TipReport.query.filter_by(tip_id=tip.id, user_id=current_user.id).first():
        db.session.add(TipReport(tip_id=tip.id, user_id=current_user.id, reason=form.reason.data))
        notify(_admin_ids(), "moderation", _("Tuyau signalé : %(t)s", t=tip.title),
               url=url_for("tips.show", tip_id=tip.id))
        db.session.commit()
    flash(_("Merci, l'administration va examiner ce tuyau."), "info")
    return redirect(url_for("tips.show", tip_id=tip.id))


@bp.route("/<int:tip_id>/supprimer", methods=["POST"])
@login_required
def delete(tip_id):
    tip = db.get_or_404(Tip, tip_id)
    if not (current_user.is_admin or tip.author_id == current_user.id) or not FlaskForm().validate_on_submit():
        abort(403)
    stored = tip.file
    db.session.delete(tip)
    if stored:
        delete_stored(stored)
    db.session.commit()
    flash(_("Tuyau supprimé."), "success")
    return redirect(url_for("tips.index"))


# --- Modération (administration) -------------------------------------------

@bp.route("/moderation")
@admin_required
def moderate():
    pending = Tip.query.filter_by(status=PENDING).order_by(Tip.created_at).all()
    reported = (Tip.query.join(TipReport).filter(Tip.status == PUBLISHED)
                .group_by(Tip.id).order_by(func.count(TipReport.id).desc()).all())
    return render_template("tips/moderate.html", pending=pending, reported=reported, categories=CATEGORY_LABELS)


@bp.route("/<int:tip_id>/moderer/<decision>", methods=["POST"])
@admin_required
def decide(tip_id, decision):
    tip = db.get_or_404(Tip, tip_id)
    form = ModerationForm()
    if decision not in ("publier", "refuser") or not form.validate_on_submit():
        abort(400)
    tip.moderated_by_id = current_user.id
    tip.moderation_note = form.note.data
    if decision == "publier":
        tip.status = PUBLISHED
        tip.published_at = tip.published_at or utcnow()
        TipReport.query.filter_by(tip_id=tip.id).delete()
        message = _("Votre tuyau « %(t)s » est publié. Merci !", t=tip.title)
    else:
        tip.status = REJECTED
        message = _("Votre tuyau « %(t)s » n'a pas été publié.", t=tip.title)
    notify([tip.author_id], "moderation", message, url=url_for("tips.show", tip_id=tip.id), exclude=current_user.id)
    db.session.commit()
    flash(_("Décision enregistrée."), "success")
    return redirect(url_for("tips.moderate"))
