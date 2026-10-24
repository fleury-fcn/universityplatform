from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from app.core.forms import none_if_empty, strip_filter

CATEGORY_LABELS = {
    "cours": _l("Cours et révisions"),
    "examens": _l("Examens"),
    "logement": _l("Logement"),
    "transport": _l("Transport"),
    "restauration": _l("Restauration"),
    "demarches": _l("Démarches administratives"),
    "stages": _l("Stages et emploi"),
    "autre": _l("Autre"),
}


class TipForm(FlaskForm):
    title = StringField(_l("Titre"), validators=[DataRequired(), Length(max=200)], filters=[strip_filter])
    category = SelectField(_l("Catégorie"), choices=list(CATEGORY_LABELS.items()))
    course_id = SelectField(_l("Cours concerné (facultatif)"), coerce=int)
    body = TextAreaField(_l("Votre conseil"), validators=[DataRequired(), Length(min=20, max=5000)])
    attachment = FileField(_l("Pièce jointe (facultatif)"))


class ModerationForm(FlaskForm):
    note = StringField(_l("Motif (envoyé à l'auteur en cas de refus)"), validators=[Optional(), Length(max=300)],
                       filters=[none_if_empty])


class ReportForm(FlaskForm):
    reason = StringField(_l("Pourquoi signaler ce tuyau ?"), validators=[DataRequired(), Length(max=300)],
                         filters=[strip_filter])
