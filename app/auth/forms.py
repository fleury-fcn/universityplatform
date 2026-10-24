from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, PasswordField, SelectField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

from app.core.forms import StrongPassword, none_if_empty, strip_filter


class LoginForm(FlaskForm):
    identifier = StringField(
        _l("Matricule, identifiant ou e-mail"), validators=[DataRequired()], filters=[strip_filter]
    )
    password = PasswordField(_l("Mot de passe"), validators=[DataRequired()])
    remember = BooleanField(_l("Rester connecté sur cet appareil"))


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(_l("Mot de passe actuel"), validators=[DataRequired()])
    new_password = PasswordField(_l("Nouveau mot de passe"), validators=[DataRequired(), StrongPassword()])
    confirm = PasswordField(
        _l("Confirmer le nouveau mot de passe"),
        validators=[DataRequired(), EqualTo("new_password", message=_l("Les mots de passe ne correspondent pas."))],
    )


class RegisterForm(FlaskForm):
    matricule = StringField(_l("Matricule"), validators=[DataRequired(), Length(max=32)], filters=[strip_filter])
    first_name = StringField(_l("Prénom"), validators=[DataRequired(), Length(max=80)], filters=[strip_filter])
    last_name = StringField(_l("Nom"), validators=[DataRequired(), Length(max=80)], filters=[strip_filter])
    email = EmailField(_l("E-mail (facultatif)"), validators=[Optional(), Email(), Length(max=254)], filters=[none_if_empty])
    promotion_id = SelectField(_l("Promotion"), coerce=int, validators=[DataRequired()])
    password = PasswordField(_l("Mot de passe"), validators=[DataRequired(), StrongPassword("matricule")])
    confirm = PasswordField(
        _l("Confirmer le mot de passe"),
        validators=[DataRequired(), EqualTo("password", message=_l("Les mots de passe ne correspondent pas."))],
    )
