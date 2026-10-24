from datetime import timedelta

from flask import abort, flash, redirect, render_template, request, url_for
from flask_babel import format_date
from flask_babel import gettext as _
from flask_login import current_user, login_required

from app.core.dates import local_today, parse_date
from app.core.security import ROLE_TEACHER, admin_required
from app.extensions import db
from app.main.widgets import home_widget
from app.models import Promotion, Room, ScheduleEntry, User
from app.models.schedule import entries_for_day, week_days
from app.services.notifications import notify, recipients

from . import bp
from .forms import EntryForm, OccurrenceForm


def _scope():
    """Ce que l'utilisateur consulte : (promotion_id, teacher_id, promotions proposées)."""
    promotions = []
    if current_user.is_staff:
        promotions = Promotion.query.filter_by(is_active=True).order_by(Promotion.name).all()
    requested = request.args.get("promotion", type=int)
    if current_user.is_student:
        return current_user.promotion_id, None, promotions
    if requested and any(p.id == requested for p in promotions):
        return requested, None, promotions
    if current_user.is_teacher:
        return None, current_user.id, promotions
    return (promotions[0].id if promotions else None), None, promotions


@home_widget(order=10)
def today_widget(user):
    if user.is_student and not user.promotion_id:
        return None
    if not (user.is_student or user.is_teacher):
        return None
    today = local_today()
    entries = entries_for_day(
        today,
        promotion_id=user.promotion_id if user.is_student else None,
        teacher_id=user.id if user.is_teacher else None,
    )
    return "schedule/_widget.html", {"entries": entries, "day": today}


@bp.route("/")
@login_required
def index():
    promotion_id, teacher_id, promotions = _scope()
    view = "semaine" if request.args.get("vue") == "semaine" else "jour"
    day = parse_date(request.args.get("date"), local_today())
    if view == "semaine":
        days = [(d, entries_for_day(d, promotion_id, teacher_id)) for d in week_days(day)]
        prev_day, next_day = day - timedelta(days=7), day + timedelta(days=7)
    else:
        days = [(day, entries_for_day(day, promotion_id, teacher_id))]
        prev_day, next_day = day - timedelta(days=1), day + timedelta(days=1)
    if not promotion_id and not teacher_id:
        days = []
    return render_template(
        "schedule/index.html", view=view, day=day, days=days, today=local_today(),
        prev_day=prev_day, next_day=next_day, promotions=promotions,
        promotion_id=promotion_id, teacher_id=teacher_id,
    )


# --- Gestion (administration) ---------------------------------------------

def _choices(form):
    if hasattr(form, "promotion_id"):
        form.promotion_id.choices = [(p.id, p.name) for p in Promotion.query.order_by(Promotion.name)]
        form.teacher_id.choices = [(0, "—")] + [
            (u.id, u.full_name)
            for u in User.query.filter_by(role=ROLE_TEACHER, is_active=True).order_by(User.last_name)
        ]
    form.room_id.choices = [(0, "—")] + [(r.id, f"{r.name} ({r.code})") for r in Room.query.order_by(Room.name)]


def _notify_change(entry, message):
    url = url_for("schedule.index", date=(entry.date or local_today()).isoformat())
    user_ids = recipients(entry.promotion_id, include_staff=False)
    if entry.teacher_id:
        user_ids.append(entry.teacher_id)
    notify(user_ids, "schedule", message, url=url, exclude=current_user.id)


@bp.route("/gestion")
@admin_required
def manage():
    promotions = Promotion.query.filter_by(is_active=True).order_by(Promotion.name).all()
    promotion_id = request.args.get("promotion", type=int) or (promotions[0].id if promotions else None)
    recurring = (
        ScheduleEntry.query.filter_by(promotion_id=promotion_id, date=None)
        .order_by(ScheduleEntry.weekday, ScheduleEntry.start_time).all()
    )
    upcoming = (
        ScheduleEntry.query.filter(ScheduleEntry.promotion_id == promotion_id, ScheduleEntry.date >= local_today())
        .order_by(ScheduleEntry.date, ScheduleEntry.start_time).all()
    )
    return render_template("schedule/manage.html", promotions=promotions, promotion_id=promotion_id,
                           recurring=recurring, upcoming=upcoming)


@bp.route("/seances/nouvelle", methods=["GET", "POST"], defaults={"entry_id": None})
@bp.route("/seances/<int:entry_id>", methods=["GET", "POST"])
@admin_required
def edit(entry_id):
    entry = db.get_or_404(ScheduleEntry, entry_id) if entry_id else None
    if entry and entry.is_change:
        return redirect(url_for("schedule.occurrence", entry_id=entry.replaces_id, day=entry.date.isoformat()))
    form = EntryForm(obj=entry)
    _choices(form)
    if request.method == "GET":
        if entry:
            form.repeat.data = "weekly" if entry.is_recurring else "once"
            form.teacher_id.data = entry.teacher_id or 0
            form.room_id.data = entry.room_id or 0
            form.weekday.data = entry.weekday if entry.weekday is not None else 0
        else:
            form.promotion_id.data = request.args.get("promotion", type=int)
    if form.validate_on_submit():
        if entry is None:
            entry = ScheduleEntry()
            db.session.add(entry)
        weekly = form.repeat.data == "weekly"
        entry.promotion_id = form.promotion_id.data
        entry.title, entry.kind, entry.note = form.title.data, form.kind.data, form.note.data
        entry.teacher_id = form.teacher_id.data or None
        entry.teacher_name = None if entry.teacher_id else form.teacher_name.data
        entry.room_id = form.room_id.data or None
        entry.weekday = form.weekday.data if weekly else None
        entry.date = None if weekly else form.date.data
        entry.valid_from = form.valid_from.data if weekly else None
        entry.valid_until = form.valid_until.data if weekly else None
        entry.start_time, entry.end_time = form.start_time.data, form.end_time.data
        db.session.flush()
        if form.notify.data:
            _notify_change(entry, _("Emploi du temps modifié : %(title)s", title=entry.title))
        db.session.commit()
        flash(_("Séance enregistrée."), "success")
        return redirect(url_for("schedule.manage", promotion=entry.promotion_id))
    return render_template("schedule/edit.html", form=form, entry=entry)


@bp.route("/seances/<int:entry_id>/supprimer", methods=["POST"])
@admin_required
def delete(entry_id):
    entry = db.get_or_404(ScheduleEntry, entry_id)
    promotion_id = entry.promotion_id
    ScheduleEntry.query.filter_by(replaces_id=entry.id).delete()
    db.session.delete(entry)
    db.session.commit()
    flash(_("Séance supprimée."), "success")
    return redirect(url_for("schedule.manage", promotion=promotion_id))


@bp.route("/seances/<int:entry_id>/le/<day>", methods=["GET", "POST"])
@admin_required
def occurrence(entry_id, day):
    base = db.get_or_404(ScheduleEntry, entry_id)
    day = parse_date(day)
    if not base.is_recurring or day is None or day.weekday() != base.weekday:
        abort(404)
    change = ScheduleEntry.query.filter_by(replaces_id=base.id, date=day).first()
    form = OccurrenceForm(obj=change or base)
    _choices(form)
    if request.method == "GET":
        form.room_id.data = (change or base).room_id or 0
        form.note.data = change.note if change else None
    if form.validate_on_submit():
        if change is None:
            change = ScheduleEntry(
                promotion_id=base.promotion_id, title=base.title, kind=base.kind, teacher_id=base.teacher_id,
                teacher_name=base.teacher_name, date=day, replaces_id=base.id,
            )
            db.session.add(change)
        change.is_cancelled = form.is_cancelled.data
        change.start_time, change.end_time = form.start_time.data, form.end_time.data
        change.room_id = form.room_id.data or None
        change.note = form.note.data
        db.session.flush()
        if form.notify.data:
            when = format_date(day, "full")
            message = (_("Séance annulée : %(title)s, %(when)s", title=base.title, when=when) if change.is_cancelled
                       else _("Séance modifiée : %(title)s, %(when)s", title=base.title, when=when))
            _notify_change(change, message)
        db.session.commit()
        flash(_("Modification enregistrée pour cette date."), "success")
        return redirect(url_for("schedule.index", date=day.isoformat(), promotion=base.promotion_id))
    return render_template("schedule/occurrence.html", form=form, base=base, day=day, change=change)


@bp.route("/seances/<int:entry_id>/le/<day>/retablir", methods=["POST"])
@admin_required
def occurrence_reset(entry_id, day):
    day = parse_date(day)
    change = ScheduleEntry.query.filter_by(replaces_id=entry_id, date=day).first_or_404()
    promotion_id = change.promotion_id
    db.session.delete(change)
    db.session.commit()
    flash(_("La séance habituelle est rétablie."), "success")
    return redirect(url_for("schedule.index", date=day.isoformat(), promotion=promotion_id))
