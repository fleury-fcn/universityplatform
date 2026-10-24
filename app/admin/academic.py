"""Administration du référentiel : départements, filières, promotions."""
import re

from flask import flash, redirect, render_template, url_for
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp, ValidationError

from app.core.forms import strip_filter
from app.core.security import admin_required
from app.extensions import db
from app.models import Department, Program, Promotion

from . import bp

CODE_VALIDATORS = [
    DataRequired(),
    Length(max=30),
    Regexp(r"^[A-Za-z0-9+_-]+$", message=_l("Lettres, chiffres, +, - et _ uniquement.")),
]


def _upper(value):
    return value.strip().upper() if isinstance(value, str) else value


class DepartmentForm(FlaskForm):
    code = StringField(_l("Code"), validators=CODE_VALIDATORS, filters=[_upper])
    name = StringField(_l("Nom"), validators=[DataRequired(), Length(max=120)], filters=[strip_filter])
    description = TextAreaField(_l("Description"), validators=[Optional(), Length(max=2000)])


class ProgramForm(FlaskForm):
    code = StringField(_l("Code"), validators=CODE_VALIDATORS, filters=[_upper])
    name = StringField(_l("Nom"), validators=[DataRequired(), Length(max=160)], filters=[strip_filter])
    cycle = SelectField(_l("Cycle"), choices=[("licence", _l("Licence (BAC)")), ("master", _l("Master"))])
    department_id = SelectField(_l("Département"), coerce=int)
    description = TextAreaField(_l("Description"), validators=[Optional(), Length(max=2000)])


class PromotionForm(FlaskForm):
    code = StringField(_l("Code"), validators=CODE_VALIDATORS, filters=[_upper])
    name = StringField(_l("Nom"), validators=[DataRequired(), Length(max=160)], filters=[strip_filter])
    level = StringField(_l("Niveau"), validators=[DataRequired(), Length(max=10)], filters=[_upper],
                        description=_l("Ex. BAC1, BAC2, BAC3, M1, M2"))
    academic_year = StringField(
        _l("Année académique"),
        validators=[DataRequired(), Regexp(r"^\d{4}-\d{4}$", message=_l("Format attendu : 2026-2027"))],
        filters=[strip_filter],
    )
    program_id = SelectField(_l("Filière"), coerce=int)
    is_active = BooleanField(_l("Promotion en cours"), default=True)

    def validate_academic_year(self, field):
        if re.match(r"^\d{4}-\d{4}$", field.data or ""):
            start, end = (int(x) for x in field.data.split("-"))
            if end != start + 1:
                raise ValidationError(_("La seconde année doit suivre la première."))


KINDS = {
    "departement": (Department, DepartmentForm, _l("Département")),
    "filiere": (Program, ProgramForm, _l("Filière")),
    "promotion": (Promotion, PromotionForm, _l("Promotion")),
}


def _set_choices(form):
    if hasattr(form, "department_id"):
        form.department_id.choices = [(d.id, d.name) for d in Department.query.order_by(Department.name)]
    if hasattr(form, "program_id"):
        form.program_id.choices = [(p.id, p.name) for p in Program.query.order_by(Program.name)]


@bp.route("/referentiel")
@admin_required
def academic():
    departments = Department.query.order_by(Department.name).all()
    return render_template("admin/academic.html", departments=departments)


@bp.route("/referentiel/<kind>/nouveau", methods=["GET", "POST"], defaults={"obj_id": None})
@bp.route("/referentiel/<kind>/<int:obj_id>", methods=["GET", "POST"])
@admin_required
def academic_edit(kind, obj_id):
    if kind not in KINDS:
        return redirect(url_for("admin.academic"))
    model, form_cls, label = KINDS[kind]
    obj = db.get_or_404(model, obj_id) if obj_id else None
    form = form_cls(obj=obj)
    _set_choices(form)
    if form.validate_on_submit():
        duplicate = model.query.filter(model.code == form.code.data)
        if obj:
            duplicate = duplicate.filter(model.id != obj.id)
        if duplicate.first():
            form.code.errors.append(_("Ce code est déjà utilisé."))
        else:
            if obj is None:
                obj = model()
                db.session.add(obj)
            form.populate_obj(obj)
            db.session.commit()
            flash(_("Enregistré."), "success")
            return redirect(url_for("admin.academic"))
    return render_template("admin/academic_form.html", form=form, obj=obj, label=label)
