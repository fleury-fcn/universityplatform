from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import EmailField, SelectField
from wtforms.validators import Email, Length, Optional

from app.core.forms import none_if_empty


class ProfileForm(FlaskForm):
    email = EmailField(_l("E-mail"), validators=[Optional(), Email(), Length(max=254)], filters=[none_if_empty])
    locale = SelectField(_l("Langue de l'application"))
