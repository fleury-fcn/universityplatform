from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length

from app.core.forms import strip_filter


class NewsForm(FlaskForm):
    title = StringField(_l("Titre"), validators=[DataRequired(), Length(max=200)], filters=[strip_filter])
    category_id = SelectField(_l("Catégorie"), coerce=int)
    promotion_id = SelectField(_l("Destinataires"), coerce=int)
    body = TextAreaField(
        _l("Texte"),
        validators=[DataRequired(), Length(max=20000)],
        description=_l("Texte simple. Laissez une ligne vide entre deux paragraphes."),
    )
    is_pinned = BooleanField(_l("Épingler en haut de la liste"))
    is_published = BooleanField(_l("Publier (les destinataires reçoivent une notification)"))


class CategoryForm(FlaskForm):
    name = StringField(_l("Nouvelle catégorie"), validators=[DataRequired(), Length(max=60)], filters=[strip_filter])
