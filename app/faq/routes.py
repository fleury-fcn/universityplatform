from itertools import groupby

from flask import flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_babel import lazy_gettext as _l
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from app.core.forms import none_if_empty, strip_filter
from app.core.security import admin_required
from app.extensions import db
from app.models import FaqEntry

from . import bp
from .search import rank


class FaqForm(FlaskForm):
    question = StringField(_l("Question"), validators=[DataRequired(), Length(max=255)], filters=[strip_filter])
    answer = TextAreaField(_l("Réponse"), validators=[DataRequired(), Length(max=5000)])
    category = StringField(_l("Rubrique"), validators=[DataRequired(), Length(max=60)], filters=[strip_filter])
    keywords = StringField(_l("Mots-clés (aident la recherche)"), validators=[Optional(), Length(max=255)],
                           filters=[none_if_empty])
    position = IntegerField(_l("Ordre d'affichage"), default=0, validators=[Optional()])


@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    entries = FaqEntry.query.order_by(FaqEntry.category, FaqEntry.position, FaqEntry.id).all()
    results = rank(entries, q) if q else []
    grouped = [(cat, list(items)) for cat, items in groupby(entries, key=lambda e: e.category)]
    return render_template("faq/index.html", q=q, results=results, grouped=grouped)


@bp.route("/gestion")
@admin_required
def manage():
    entries = FaqEntry.query.order_by(FaqEntry.category, FaqEntry.position).all()
    return render_template("faq/manage.html", entries=entries, csrf_form=FlaskForm())


@bp.route("/nouvelle", methods=["GET", "POST"], defaults={"entry_id": None})
@bp.route("/<int:entry_id>/modifier", methods=["GET", "POST"])
@admin_required
def edit(entry_id):
    entry = db.get_or_404(FaqEntry, entry_id) if entry_id else None
    form = FaqForm(obj=entry)
    if form.validate_on_submit():
        if entry is None:
            entry = FaqEntry()
            db.session.add(entry)
        form.populate_obj(entry)
        entry.position = entry.position or 0
        db.session.commit()
        flash(_("Question enregistrée."), "success")
        return redirect(url_for("faq.manage"))
    return render_template("faq/edit.html", form=form, entry=entry)


@bp.route("/<int:entry_id>/supprimer", methods=["POST"])
@admin_required
def delete(entry_id):
    entry = db.get_or_404(FaqEntry, entry_id)
    if FlaskForm().validate_on_submit():
        db.session.delete(entry)
        db.session.commit()
        flash(_("Question supprimée."), "success")
    return redirect(url_for("faq.manage"))
