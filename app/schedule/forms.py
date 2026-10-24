from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, SelectField, StringField, TimeField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from app.core.forms import none_if_empty, strip_filter

WEEKDAYS = [
    (0, _l("Lundi")), (1, _l("Mardi")), (2, _l("Mercredi")),
    (3, _l("Jeudi")), (4, _l("Vendredi")), (5, _l("Samedi")), (6, _l("Dimanche")),
]
KIND_CHOICES = [
    ("CM", _l("Cours magistral")), ("TD", _l("Travaux dirigés")), ("TP", _l("Travaux pratiques")),
    ("EXAMEN", _l("Examen")), ("AUTRE", _l("Autre")),
]


def _check_times(form):
    if form.start_time.data and form.end_time.data and form.end_time.data <= form.start_time.data:
        raise ValidationError(_l("L'heure de fin doit être après l'heure de début."))


class EntryForm(FlaskForm):
    promotion_id = SelectField(_l("Promotion"), coerce=int)
    title = StringField(_l("Intitulé"), validators=[DataRequired(), Length(max=160)], filters=[strip_filter])
    kind = SelectField(_l("Type"), choices=KIND_CHOICES)
    teacher_id = SelectField(_l("Enseignant (compte)"), coerce=int)
    teacher_name = StringField(
        _l("Enseignant (texte libre)"), validators=[Optional(), Length(max=120)], filters=[none_if_empty],
        description=_l("Si l'enseignant n'a pas de compte."),
    )
    room_id = SelectField(_l("Salle"), coerce=int)
    repeat = SelectField(_l("Fréquence"), choices=[("weekly", _l("Chaque semaine")), ("once", _l("Une seule fois"))])
    weekday = SelectField(_l("Jour"), coerce=int, choices=WEEKDAYS)
    date = DateField(_l("Date (séance unique)"), validators=[Optional()])
    start_time = TimeField(_l("Début"), validators=[DataRequired()])
    end_time = TimeField(_l("Fin"), validators=[DataRequired()])
    valid_from = DateField(_l("À partir du"), validators=[Optional()])
    valid_until = DateField(_l("Jusqu'au"), validators=[Optional()])
    note = StringField(_l("Remarque"), validators=[Optional(), Length(max=200)], filters=[none_if_empty])
    notify = BooleanField(_l("Prévenir les étudiants concernés"), default=True)

    def validate_end_time(self, field):
        _check_times(self)

    def validate_date(self, field):
        if self.repeat.data == "once" and not field.data:
            raise ValidationError(_l("Indiquez la date de la séance."))

    def validate_valid_until(self, field):
        if field.data and self.valid_from.data and field.data < self.valid_from.data:
            raise ValidationError(_l("La date de fin doit suivre la date de début."))


class OccurrenceForm(FlaskForm):
    """Modifier ou annuler une seule occurrence d'une séance hebdomadaire."""

    is_cancelled = BooleanField(_l("Annuler cette séance"))
    start_time = TimeField(_l("Début"), validators=[DataRequired()])
    end_time = TimeField(_l("Fin"), validators=[DataRequired()])
    room_id = SelectField(_l("Salle"), coerce=int)
    note = StringField(_l("Remarque (motif, consignes...)"), validators=[Optional(), Length(max=200)],
                       filters=[none_if_empty])
    notify = BooleanField(_l("Prévenir les étudiants concernés"), default=True)

    def validate_end_time(self, field):
        _check_times(self)
