from datetime import timedelta

from flask import abort, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from sqlalchemy import or_

from app.core.files import UploadError, access_rule, accept_attribute, category_rules, delete_stored, save_upload
from app.core.security import ROLE_STUDENT, no_store
from app.extensions import db
from app.models import Message, MessageRecipient, Promotion, User, utcnow
from app.services.notifications import mark_read, notify

from . import bp
from .forms import ComposeForm

MAX_ATTACHMENTS = 3
MAX_RECIPIENTS_STUDENT = 20
MAX_MESSAGES_PER_HOUR = 30
PER_PAGE = 25


def _uploads(form):
    return [f for f in (form.attachments.data or []) if f and f.filename]


@access_rule("message")
def _can_download_attachment(user, stored):
    from app.models.messages import message_attachments

    message_ids = [row.message_id for row in
                   db.session.execute(db.select(message_attachments.c.message_id)
                                      .where(message_attachments.c.file_id == stored.id))]
    return any(db.session.get(Message, mid).can_read(user) for mid in message_ids)


@bp.route("/")
@login_required
@no_store
def inbox():
    page = (MessageRecipient.query.filter_by(user_id=current_user.id, deleted_at=None)
            .join(Message).order_by(Message.created_at.desc()).paginate(per_page=PER_PAGE, error_out=False))
    return render_template("messages/inbox.html", page=page, box="inbox")


@bp.route("/envoyes")
@login_required
@no_store
def sent():
    page = (Message.query.filter_by(sender_id=current_user.id, sender_deleted_at=None)
            .order_by(Message.created_at.desc()).paginate(per_page=PER_PAGE, error_out=False))
    return render_template("messages/sent.html", page=page, box="sent")


@bp.route("/<int:message_id>")
@login_required
@no_store
def show(message_id):
    message = db.get_or_404(Message, message_id)
    if not message.can_read(current_user):
        abort(404)
    entry = message.recipient_entry(current_user)
    if entry and entry.read_at is None:
        entry.read_at = utcnow()
        mark_read(current_user.id, url=url_for("messages.show", message_id=message.id))
        db.session.commit()
    return render_template("messages/show.html", message=message, csrf_form=FlaskForm())


@bp.route("/annuaire")
@login_required
def directory():
    q = request.args.get("q", "").strip()
    people = []
    if len(q) >= 2:
        like = f"%{q}%"
        people = (User.query.filter(User.is_active.is_(True), User.id != current_user.id,
                                    or_(User.first_name.ilike(like), User.last_name.ilike(like),
                                        User.matricule.ilike(like)))
                  .order_by(User.last_name, User.first_name).limit(30).all())
    return render_template("messages/directory.html", q=q, people=people)


def _recipients_from_request():
    ids = {int(v) for v in request.values.getlist("to") if v.isdigit()}
    if not ids:
        return []
    return User.query.filter(User.id.in_(ids), User.is_active.is_(True), User.id != current_user.id).all()


@bp.route("/nouveau", methods=["GET", "POST"])
@login_required
@no_store
def compose():
    form = ComposeForm()
    promotions = Promotion.query.filter_by(is_active=True).order_by(Promotion.name).all() if current_user.is_staff else []
    form.promotion_id.choices = [(0, "—")] + [(p.id, p.name) for p in promotions]
    recipients = _recipients_from_request()
    reply_to = None
    if request.args.get("repondre", type=int):
        reply_to = db.session.get(Message, request.args.get("repondre", type=int))
        if reply_to is None or not reply_to.can_read(current_user):
            abort(404)
        if request.method == "GET":
            recipients = [reply_to.sender] if reply_to.sender_id != current_user.id else recipients
            subject = reply_to.subject
            form.subject.data = subject if subject.lower().startswith("re:") else f"Re: {subject}"

    if form.validate_on_submit():
        error = _check_compose(form, recipients)
        stored_files = []
        if not error:
            try:
                for upload in _uploads(form):
                    stored_files.append(save_upload(upload, "message", current_user.id))
            except UploadError as err:
                error = str(err)
                for stored in stored_files:
                    delete_stored(stored)
        if error:
            flash(error, "danger")
        else:
            message = _send(form, recipients, stored_files, reply_to)
            flash(_("Message envoyé."), "success")
            return redirect(url_for("messages.show", message_id=message.id))

    max_bytes = category_rules("message")[1]
    return render_template("messages/compose.html", form=form, recipients=recipients, reply_to=reply_to,
                           accept=accept_attribute("message"), max_bytes=max_bytes, max_attachments=MAX_ATTACHMENTS)


def _check_compose(form, recipients):
    promotion_id = form.promotion_id.data if current_user.is_staff else 0
    if not recipients and not promotion_id:
        return _("Choisissez au moins un destinataire.")
    if current_user.role == ROLE_STUDENT and len(recipients) > MAX_RECIPIENTS_STUDENT:
        return _("%(n)d destinataires au maximum.", n=MAX_RECIPIENTS_STUDENT)
    if len(_uploads(form)) > MAX_ATTACHMENTS:
        return _("%(n)d pièces jointes au maximum.", n=MAX_ATTACHMENTS)
    recent = Message.query.filter(Message.sender_id == current_user.id,
                                  Message.created_at > utcnow() - timedelta(hours=1)).count()
    if recent >= MAX_MESSAGES_PER_HOUR:
        return _("Trop de messages envoyés récemment. Réessayez plus tard.")
    return None


def _send(form, recipients, stored_files, reply_to):
    promotion_id = (form.promotion_id.data or None) if current_user.is_staff else None
    user_ids = {u.id for u in recipients}
    if promotion_id:
        user_ids |= {uid for (uid,) in db.session.query(User.id).filter_by(promotion_id=promotion_id, is_active=True)}
    user_ids.discard(current_user.id)
    message = Message(sender_id=current_user.id, subject=form.subject.data, body=form.body.data.strip(),
                      promotion_id=promotion_id, reply_to_id=reply_to.id if reply_to else None,
                      attachments=stored_files)
    message.recipients = [MessageRecipient(user_id=uid) for uid in user_ids]
    db.session.add(message)
    db.session.flush()
    notify(user_ids, "message", _("Message de %(name)s : %(subject)s", name=current_user.full_name,
                                  subject=message.subject),
           url=url_for("messages.show", message_id=message.id))
    db.session.commit()
    return message


@bp.route("/<int:message_id>/supprimer", methods=["POST"])
@login_required
def delete(message_id):
    message = db.get_or_404(Message, message_id)
    if not FlaskForm().validate_on_submit() or not message.can_read(current_user):
        abort(404)
    now = utcnow()
    entry = message.recipient_entry(current_user)
    if entry and entry.deleted_at is None:
        entry.deleted_at = now
        target = url_for("messages.inbox")
    else:
        message.sender_deleted_at = now
        target = url_for("messages.sent")
    # Plus personne ne le voit : on supprime réellement le message et ses pièces jointes.
    if message.sender_deleted_at and all(r.deleted_at for r in message.recipients):
        files = list(message.attachments)
        db.session.delete(message)
        db.session.flush()
        for stored in files:
            delete_stored(stored)
    db.session.commit()
    flash(_("Message supprimé."), "success")
    return redirect(target)
