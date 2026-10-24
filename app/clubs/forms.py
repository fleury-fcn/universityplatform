from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from app.core.forms import none_if_empty, strip_filter

CATEGORY_LABELS = {
    "science": _l("Sciences"),
    "technologie": _l("Technologie"),
    "social": _l("Société et langues"),
    "culture": _l("Culture"),
    "entrepreneuriat": _l("Entrepreneuriat"),
    "sport": _l("Sport"),
    "autre": _l("Autre"),
}


class ClubForm(FlaskForm):
    name = StringField(_l("Nom"), validators=[DataRequired(), Length(max=120)], filters=[strip_filter])
    category = SelectField(_l("Catégorie"), choices=list(CATEGORY_LABELS.items()))
    description = TextAreaField(_l("Présentation"), validators=[DataRequired(), Length(max=5000)])
    meeting_frequency = StringField(_l("Fréquence des réunions"), validators=[Optional(), Length(max=80)],
                                    filters=[none_if_empty])
    tags = StringField(_l("Thèmes (séparés par des virgules)"), validators=[Optional(), Length(max=255)],
                       filters=[none_if_empty])
    contact = StringField(_l("Contact"), validators=[Optional(), Length(max=200)], filters=[none_if_empty])
    is_active = BooleanField(_l("Club actif"), default=True)


class AnnouncementForm(FlaskForm):
    body = TextAreaField(_l("Annonce aux membres"), validators=[DataRequired(), Length(max=3000)])


class LeaderForm(FlaskForm):
    identifier = StringField(_l("Matricule ou identifiant du responsable"), validators=[DataRequired()],
                             filters=[strip_filter])
