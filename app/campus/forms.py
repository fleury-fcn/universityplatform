from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import FloatField, IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.core.forms import none_if_empty, strip_filter

KIND_LABELS = {
    "amphi": _l("Amphithéâtre"),
    "salle": _l("Salle de cours"),
    "labo": _l("Laboratoire"),
    "bibliotheque": _l("Bibliothèque"),
    "bureau": _l("Bureau"),
    "service": _l("Service"),
    "autre": _l("Autre"),
}


class RoomForm(FlaskForm):
    code = StringField(_l("Code"), validators=[DataRequired(), Length(max=30)],
                       filters=[lambda v: v.strip().upper() if v else v])
    name = StringField(_l("Nom"), validators=[DataRequired(), Length(max=120)], filters=[strip_filter])
    kind = SelectField(_l("Type"), choices=list(KIND_LABELS.items()))
    building = StringField(_l("Bâtiment"), validators=[Optional(), Length(max=120)], filters=[none_if_empty])
    floor = StringField(_l("Étage"), validators=[Optional(), Length(max=30)], filters=[none_if_empty])
    capacity = IntegerField(_l("Capacité (places)"), validators=[Optional(), NumberRange(min=0, max=5000)])
    description = TextAreaField(_l("Comment s'y rendre, équipements..."), validators=[Optional(), Length(max=2000)])
    latitude = FloatField(_l("Latitude"), validators=[Optional(), NumberRange(min=-90, max=90)])
    longitude = FloatField(_l("Longitude"), validators=[Optional(), NumberRange(min=-180, max=180)])


class MapForm(FlaskForm):
    title = StringField(_l("Titre du plan"), validators=[DataRequired(), Length(max=120)], filters=[strip_filter])
    image = FileField(_l("Image (PNG ou JPEG, 5 Mo maximum)"), validators=[FileRequired()])
