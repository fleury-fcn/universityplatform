from flask import current_app, flash, make_response, redirect, render_template, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required

from app.core.security import no_store
from app.extensions import db
from app.models import User

from . import bp
from .forms import ProfileForm


@bp.route("/profil")
@login_required
@no_store
def show():
    return render_template("profile/show.html", user=current_user)


@bp.route("/profil/modifier", methods=["GET", "POST"])
@login_required
@no_store
def edit():
    form = ProfileForm(obj=current_user)
    form.locale.choices = list(current_app.config["LANGUAGES"].items())
    if form.validate_on_submit():
        email = form.email.data.lower() if form.email.data else None
        if email and User.query.filter(User.email == email, User.id != current_user.id).first():
            form.email.errors.append(_("Cet e-mail est déjà utilisé."))
        else:
            current_user.email = email
            current_user.locale = form.locale.data
            db.session.commit()
            flash(_("Profil mis à jour."), "success")
            response = make_response(redirect(url_for("profile.show")))
            response.set_cookie("lang", form.locale.data, max_age=365 * 24 * 3600, samesite="Lax", httponly=True)
            return response
    if not form.locale.data:
        form.locale.data = current_user.locale or current_app.config["BABEL_DEFAULT_LOCALE"]
    return render_template("profile/edit.html", form=form)
