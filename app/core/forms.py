"""Validateurs de formulaires partagés."""
from flask_babel import lazy_gettext as _l
from wtforms.validators import ValidationError

MIN_PASSWORD_LENGTH = 8


class StrongPassword:
    """Au moins 8 caractères, pas uniquement des chiffres, différent de l'identifiant."""

    def __init__(self, identifier_field=None):
        self.identifier_field = identifier_field

    def __call__(self, form, field):
        value = field.data or ""
        if len(value) < MIN_PASSWORD_LENGTH:
            raise ValidationError(_l("Au moins %(n)d caractères.", n=MIN_PASSWORD_LENGTH))
        if value.isdigit():
            raise ValidationError(_l("Le mot de passe ne doit pas contenir uniquement des chiffres."))
        if self.identifier_field:
            identifier = getattr(form, self.identifier_field).data or ""
            if identifier and value.lower() == identifier.lower():
                raise ValidationError(_l("Le mot de passe doit être différent de l'identifiant."))


def strip_filter(value):
    return value.strip() if isinstance(value, str) else value


def none_if_empty(value):
    value = strip_filter(value)
    return value or None
