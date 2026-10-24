from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import BooleanField, IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Optional

from app.core.forms import none_if_empty, strip_filter

CATEGORY_LABELS = {
    "statistique": _l("Statistique"),
    "probabilite": _l("Probabilités"),
    "actuariat": _l("Actuariat"),
    "economie": _l("Économie"),
    "data-science": _l("Science des données"),
    "informatique": _l("Informatique"),
    "mathematiques": _l("Mathématiques"),
    "divers": _l("Divers"),
}


class BookForm(FlaskForm):
    title = StringField(_l("Titre"), validators=[DataRequired(), Length(max=255)], filters=[strip_filter])
    author = StringField(_l("Auteur(s)"), validators=[DataRequired(), Length(max=255)], filters=[strip_filter])
    category = SelectField(_l("Catégorie"), choices=list(CATEGORY_LABELS.items()))
    language = SelectField(_l("Langue"), choices=[("fr", "Français"), ("en", "English"), ("rn", "Ikirundi"),
                                                  ("sw", "Kiswahili")])
    isbn = StringField(_l("ISBN"), validators=[Optional(), Length(max=20)], filters=[none_if_empty])
    publisher = StringField(_l("Éditeur"), validators=[Optional(), Length(max=120)], filters=[none_if_empty])
    year = IntegerField(_l("Année de publication"), validators=[Optional(), NumberRange(min=1500, max=2100)])
    call_number = StringField(_l("Cote (emplacement en rayon)"), validators=[Optional(), Length(max=40)],
                              filters=[none_if_empty])
    copies_total = IntegerField(_l("Nombre d'exemplaires papier"), default=1,
                                validators=[InputRequired(message=_l("Indiquez un nombre (0 si numérique seulement).")),
                                            NumberRange(min=0, max=500)])
    description = TextAreaField(_l("Résumé"), validators=[Optional(), Length(max=5000)])
    pdf = FileField(_l("Version numérique (PDF, facultatif)"))
    remove_pdf = BooleanField(_l("Retirer la version numérique actuelle"))
