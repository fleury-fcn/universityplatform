"""Emploi du temps : séances hebdomadaires et modifications ponctuelles."""
from datetime import timedelta

from app.extensions import db

from . import TimestampMixin

SESSION_KINDS = ("CM", "TD", "TP", "EXAMEN", "AUTRE")


class ScheduleEntry(TimestampMixin, db.Model):
    """Une séance.

    - récurrente : `weekday` renseigné (0 = lundi), entre `valid_from` et `valid_until` ;
    - ponctuelle : `date` renseignée. Si `replaces_id` pointe une séance récurrente,
      elle la remplace ce jour-là (déplacement) ou l'annule (`is_cancelled`).
    """

    __tablename__ = "schedule_entries"

    id = db.Column(db.Integer, primary_key=True)
    promotion_id = db.Column(db.Integer, db.ForeignKey("promotions.id"), nullable=False, index=True)
    title = db.Column(db.String(160), nullable=False)
    kind = db.Column(db.String(10), nullable=False, default="CM")
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    teacher_name = db.Column(db.String(120))
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"))
    weekday = db.Column(db.Integer)
    date = db.Column(db.Date, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    valid_from = db.Column(db.Date)
    valid_until = db.Column(db.Date)
    replaces_id = db.Column(db.Integer, db.ForeignKey("schedule_entries.id", ondelete="CASCADE"))
    is_cancelled = db.Column(db.Boolean, nullable=False, default=False)
    note = db.Column(db.String(200))
    is_demo = db.Column(db.Boolean, nullable=False, default=False)

    promotion = db.relationship("Promotion")
    teacher = db.relationship("User")
    room = db.relationship("Room")
    replaces = db.relationship("ScheduleEntry", remote_side=[id])

    @property
    def is_recurring(self):
        return self.weekday is not None and self.date is None

    @property
    def teacher_display(self):
        return self.teacher.full_name if self.teacher else self.teacher_name

    @property
    def is_change(self):
        return self.replaces_id is not None


def entries_for_day(day, promotion_id=None, teacher_id=None):
    """Séances d'un jour, modifications ponctuelles appliquées, triées par heure."""
    base = ScheduleEntry.query
    if promotion_id:
        base = base.filter(ScheduleEntry.promotion_id == promotion_id)
    if teacher_id:
        base = base.filter(ScheduleEntry.teacher_id == teacher_id)

    recurring = base.filter(
        ScheduleEntry.weekday == day.weekday(),
        ScheduleEntry.date.is_(None),
        db.or_(ScheduleEntry.valid_from.is_(None), ScheduleEntry.valid_from <= day),
        db.or_(ScheduleEntry.valid_until.is_(None), ScheduleEntry.valid_until >= day),
    ).all()
    one_off = base.filter(ScheduleEntry.date == day).all()
    replaced = {e.replaces_id for e in one_off if e.replaces_id}
    entries = [e for e in recurring if e.id not in replaced] + one_off
    return sorted(entries, key=lambda e: (e.start_time, e.title))


def week_days(day, days=6):
    """Du lundi au samedi de la semaine contenant `day`."""
    monday = day - timedelta(days=day.weekday())
    return [monday + timedelta(days=i) for i in range(days)]
