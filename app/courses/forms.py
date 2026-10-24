from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Regexp

from app.core.forms import none_if_empty, strip_filter

KIND_LABELS = {
    "support": _l("Supports de cours"),
    "td": _l("Travaux dirigés"),
    "tp": _l("Travaux pratiques"),
    "examen": _l("Anciens sujets d'examen"),
    "corrige": _l("Corrigés"),
    "autre": _l("Autres documents"),
}


class CourseForm(FlaskForm):
    code = StringField(_l("Code"), validators=[DataRequired(), Length(max=30)],
                       filters=[lambda v: v.strip().upper() if v else v])
    title = StringField(_l("Intitulé"), validators=[DataRequired(), Length(max=200)], filters=[strip_filter])
    promotion_id = SelectField(_l("Promotion"), coerce=int)
    semester = SelectField(_l("Semestre"), coerce=int, choices=[(1, _l("Semestre 1")), (2, _l("Semestre 2"))])
    credits = IntegerField(_l("Crédits"), validators=[Optional(), NumberRange(min=0, max=60)])
    teacher_id = SelectField(_l("Enseignant responsable"), coerce=int)
    description = TextAreaField(_l("Description"), validators=[Optional(), Length(max=5000)])


class ResourceForm(FlaskForm):
    title = StringField(_l("Titre"), validators=[DataRequired(), Length(max=200)], filters=[strip_filter])
    kind = SelectField(_l("Type"), choices=list(KIND_LABELS.items()))
    academic_year = StringField(
        _l("Année académique (facultatif)"),
        validators=[Optional(), Regexp(r"^\d{4}-\d{4}$", message=_l("Format attendu : 2025-2026"))],
        filters=[none_if_empty],
    )
    file = FileField(_l("Fichier"), validators=[FileRequired()])
