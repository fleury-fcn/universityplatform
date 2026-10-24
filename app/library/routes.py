from datetime import timedelta

from flask import abort, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from sqlalchemy import func, or_

from app.core.dates import local_today
from app.core.files import UploadError, access_rule, accept_attribute, delete_stored, save_upload
from app.core.security import admin_required
from app.extensions import db
from app.models.library import (
    ACTIVE_STATUSES, BORROWED, CANCELLED, HOLDING_STATUSES, MAX_ACTIVE_RESERVATIONS, PENDING, READY, REFUSED,
    RETURNED, Book, Reservation,
)
from app.services.notifications import notify

from . import bp
from .forms import CATEGORY_LABELS, BookForm

LOAN_DAYS = 14
PER_PAGE = 20

STATUS_LABELS = {
    PENDING: _l("Demande envoyée"), READY: _l("Prêt à retirer"), BORROWED: _l("Emprunté"),
    RETURNED: _l("Rendu"), CANCELLED: _l("Annulée"), REFUSED: _l("Refusée"),
}
BOOK_FIELDS = ("title", "author", "category", "language", "isbn", "publisher", "year", "call_number",
               "copies_total", "description")

# Transitions autorisées pour la bibliothèque : action -> (statuts de départ, statut d'arrivée)
TRANSITIONS = {
    "prete": ((PENDING,), READY),
    "empruntee": ((PENDING, READY), BORROWED),
    "rendue": ((BORROWED,), RETURNED),
    "refusee": ((PENDING, READY), REFUSED),
}


@access_rule("book")
def _can_download_book(user, stored):
    return Book.query.filter_by(file_id=stored.id).first() is not None


def _held_counts(book_ids):
    rows = (db.session.query(Reservation.book_id, func.count())
            .filter(Reservation.book_id.in_(book_ids), Reservation.status.in_(HOLDING_STATUSES))
            .group_by(Reservation.book_id))
    return dict(rows.all())


@bp.app_template_global()
def reservation_label(status):
    return STATUS_LABELS.get(status, status)


@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    category = request.args.get("categorie", "")
    query = Book.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Book.title.ilike(like), Book.author.ilike(like), Book.isbn.ilike(like)))
    if category in CATEGORY_LABELS:
        query = query.filter(Book.category == category)
    page = query.order_by(Book.title).paginate(per_page=PER_PAGE, error_out=False)
    held = _held_counts([b.id for b in page.items])
    return render_template("library/index.html", page=page, held=held, q=q, category=category,
                           categories=CATEGORY_LABELS)


@bp.route("/<int:book_id>")
@login_required
def show(book_id):
    book = db.get_or_404(Book, book_id)
    mine = Reservation.query.filter(Reservation.book_id == book.id, Reservation.user_id == current_user.id,
                                    Reservation.status.in_(ACTIVE_STATUSES)).first()
    return render_template("library/show.html", book=book, mine=mine, categories=CATEGORY_LABELS,
                           form=FlaskForm())


@bp.route("/<int:book_id>/reserver", methods=["POST"])
@login_required
def reserve(book_id):
    book = db.get_or_404(Book, book_id)
    if not FlaskForm().validate_on_submit():
        abort(400)
    active = Reservation.query.filter(Reservation.user_id == current_user.id,
                                      Reservation.status.in_(ACTIVE_STATUSES))
    if active.filter(Reservation.book_id == book.id).first():
        flash(_("Vous avez déjà une réservation en cours pour ce livre."), "warning")
    elif active.count() >= MAX_ACTIVE_RESERVATIONS:
        flash(_("Vous avez atteint la limite de %(n)d réservations en cours.", n=MAX_ACTIVE_RESERVATIONS), "warning")
    elif book.copies_total <= 0:
        flash(_("Ce livre n'est disponible qu'en version numérique."), "warning")
    else:
        db.session.add(Reservation(book=book, user_id=current_user.id))
        db.session.commit()
        flash(_("Demande envoyée. Vous serez prévenu quand le livre sera prêt à retirer."), "success")
    return redirect(url_for("library.show", book_id=book.id))


@bp.route("/mes-reservations")
@login_required
def my_reservations():
    reservations = (Reservation.query.filter_by(user_id=current_user.id)
                    .order_by(Reservation.created_at.desc()).limit(50).all())
    return render_template("library/mine.html", reservations=reservations, today=local_today(), form=FlaskForm())


@bp.route("/reservations/<int:reservation_id>/annuler", methods=["POST"])
@login_required
def cancel(reservation_id):
    reservation = db.get_or_404(Reservation, reservation_id)
    if not FlaskForm().validate_on_submit():
        abort(400)
    if reservation.user_id != current_user.id and not current_user.is_admin:
        abort(404)
    if reservation.status not in (PENDING, READY):
        flash(_("Cette réservation ne peut plus être annulée."), "warning")
    else:
        reservation.status = CANCELLED
        db.session.commit()
        flash(_("Réservation annulée."), "success")
    if request.form.get("next") == "gestion":
        return redirect(url_for("library.reservations"))
    return redirect(url_for("library.my_reservations"))


# --- Gestion (administration) ---------------------------------------------

@bp.route("/gestion/reservations")
@admin_required
def reservations():
    status = request.args.get("statut", PENDING)
    query = Reservation.query
    if status == "actives":
        query = query.filter(Reservation.status.in_(ACTIVE_STATUSES))
    elif status in STATUS_LABELS:
        query = query.filter(Reservation.status == status)
    items = query.order_by(Reservation.created_at).limit(200).all()
    counts = dict(db.session.query(Reservation.status, func.count()).group_by(Reservation.status).all())
    return render_template("library/reservations.html", items=items, status=status, counts=counts,
                           today=local_today(), form=FlaskForm())


@bp.route("/gestion/reservations/<int:reservation_id>/<action>", methods=["POST"])
@admin_required
def update_reservation(reservation_id, action):
    reservation = db.get_or_404(Reservation, reservation_id)
    if action not in TRANSITIONS or not FlaskForm().validate_on_submit():
        abort(400)
    allowed_from, new_status = TRANSITIONS[action]
    book = reservation.book
    if reservation.status not in allowed_from:
        flash(_("Action impossible pour cette réservation."), "warning")
    elif (new_status in HOLDING_STATUSES and reservation.status not in HOLDING_STATUSES
          and book.copies_available <= 0):
        flash(_("Aucun exemplaire disponible."), "danger")
    else:
        reservation.status = new_status
        if new_status == BORROWED:
            reservation.due_date = local_today() + timedelta(days=LOAN_DAYS)
        messages = {
            READY: _("« %(t)s » est prêt : vous pouvez venir le retirer à la bibliothèque.", t=book.title),
            BORROWED: _("Emprunt de « %(t)s » enregistré.", t=book.title),
            RETURNED: _("Retour de « %(t)s » enregistré. Merci !", t=book.title),
            REFUSED: _("Votre demande pour « %(t)s » n'a pas pu être satisfaite.", t=book.title),
        }
        notify([reservation.user_id], "library", messages[new_status], url=url_for("library.my_reservations"))
        db.session.commit()
        flash(_("Réservation mise à jour."), "success")
    return redirect(url_for("library.reservations", statut=request.args.get("statut", PENDING)))


@bp.route("/gestion/livres/nouveau", methods=["GET", "POST"], defaults={"book_id": None})
@bp.route("/gestion/livres/<int:book_id>", methods=["GET", "POST"])
@admin_required
def edit(book_id):
    book = db.get_or_404(Book, book_id) if book_id else None
    form = BookForm(obj=book)
    if form.validate_on_submit():
        stored = None
        if form.pdf.data:
            try:
                stored = save_upload(form.pdf.data, "book", current_user.id)
            except UploadError as err:
                form.pdf.errors.append(str(err))
        if not form.pdf.errors:
            if book is None:
                book = Book()
                db.session.add(book)
            for name in BOOK_FIELDS:
                setattr(book, name, getattr(form, name).data)
            old_file = book.file
            if stored or (form.remove_pdf.data and old_file):
                book.file = stored
                if old_file:
                    delete_stored(old_file)
            db.session.commit()
            flash(_("Livre enregistré."), "success")
            return redirect(url_for("library.show", book_id=book.id))
    return render_template("library/edit.html", form=form, book=book, accept=accept_attribute("book"))


@bp.route("/gestion/livres/<int:book_id>/supprimer", methods=["POST"])
@admin_required
def delete(book_id):
    book = db.get_or_404(Book, book_id)
    if any(r.status in HOLDING_STATUSES for r in book.reservations):
        flash(_("Impossible : des exemplaires sont prêtés ou réservés."), "danger")
        return redirect(url_for("library.show", book_id=book.id))
    stored = book.file
    db.session.delete(book)
    if stored:
        delete_stored(stored)
    db.session.commit()
    flash(_("Livre supprimé."), "success")
    return redirect(url_for("library.index"))


@bp.route("/gestion")
@admin_required
def manage():
    return redirect(url_for("library.reservations"))
