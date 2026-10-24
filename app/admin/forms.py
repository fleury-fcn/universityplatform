import re

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import BooleanField, EmailField, SelectField, StringField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError

from app.core.forms import none_if_empty, strip_filter
from app.core.security import ROLE_ADMIN, ROLE_STUDENT, ROLE_TEACHER

USERNAME_RE = re.compile(r"^[a-zA-Z0-9._-]+$")

ROLE_CHOICES = [
    (ROLE_STUDENT, _l("Étudiant·e")),
    (ROLE_TEACHER, _l("Enseignant·e")),
    (ROLE_ADMIN, _l("Administration")),
]


class UserForm(FlaskForm):
    role = SelectField(_l("Rôle"), choices=ROLE_CHOICES)
    first_name = StringField(_l("Prénom"), validators=[DataRequired(), Length(max=80)], filters=[strip_filter])
    last_name = StringField(_l("Nom"), validators=[DataRequired(), Length(max=80)], filters=[strip_filter])
    # Pas de validateur Optional() ici : il interromprait les règles validate_* ci-dessous.
    username = StringField(_l("Identifiant de connexion"), validators=[Length(max=64)], filters=[none_if_empty])
    matricule = StringField(_l("Matricule"), validators=[Length(max=32)], filters=[none_if_empty])
    email = EmailField(_l("E-mail"), validators=[Optional(), Email(), Length(max=254)], filters=[none_if_empty])
    promotion_id = SelectField(_l("Promotion"), coerce=int, validators=[Optional()])
    is_active = BooleanField(_l("Compte actif"), default=True)

    def validate_matricule(self, field):
        if self.role.data == ROLE_STUDENT and not field.data:
            raise ValidationError(_l("Le matricule est obligatoire pour un étudiant."))

    def validate_username(self, field):
        if not field.data:
            if not self.matricule.data:
                raise ValidationError(_l("Indiquez un identifiant ou un matricule."))
        elif len(field.data) < 3 or not USERNAME_RE.match(field.data):
            raise ValidationError(_l("Au moins 3 caractères : lettres, chiffres, point, tiret ou tiret bas."))


class ImportUsersForm(FlaskForm):
    file = FileField(
        _l("Fichier CSV"),
        validators=[FileRequired(), FileAllowed(["csv", "txt"], _l("Fichier CSV uniquement."))],
    )
