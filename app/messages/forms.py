from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length

from app.core.forms import strip_filter


class ComposeForm(FlaskForm):
    promotion_id = SelectField(_l("Envoyer à toute une promotion (facultatif)"), coerce=int)
    subject = StringField(_l("Objet"), validators=[DataRequired(), Length(max=200)], filters=[strip_filter])
    body = TextAreaField(_l("Message"), validators=[DataRequired(), Length(max=10000)])
    attachments = MultipleFileField(_l("Pièces jointes (3 au maximum)"))
