from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required, login_user, logout_user

from app.core.security import ROLE_STUDENT, is_safe_redirect, no_store
from app.extensions import db
from app.models import Promotion, User

from . import bp
from .forms import ChangePasswordForm, LoginForm, RegisterForm

# Vues accessibles tant que le mot de passe provisoire n'a pas été changé.
_ALLOWED_WITH_TEMP_PASSWORD = {"auth.change_password", "auth.logout", "static", "main.set_language",
                               "main.service_worker", "main.manifest", "main.offline", "main.health"}


@bp.before_app_request
def enforce_password_change():
    if (
        current_user.is_authenticated
        and current_user.must_change_password
        and request.endpoint not in _ALLOWED_WITH_TEMP_PASSWORD
    ):
        return redirect(url_for("auth.change_password"))


@bp.route("/connexion", methods=["GET", "POST"])
@no_store
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_login(form.identifier.data)
        if user is None:
            User.burn_password_check(form.password.data)
        elif user.is_locked:
            flash(_("Trop de tentatives. Réessayez dans quelques minutes."), "danger")
            return render_template("auth/login.html", form=form), 429
        elif user.check_password(form.password.data):
            if not user.is_active:
                flash(_("Votre compte n'est pas encore activé par l'administration."), "warning")
                return render_template("auth/login.html", form=form)
            user.register_successful_login()
            db.session.commit()
            login_user(user, remember=form.remember.data)
            target = request.args.get("next")
            return redirect(target if is_safe_redirect(target) else url_for("main.home"))
        else:
            user.register_failed_login()
            db.session.commit()
        flash(_("Identifiant ou mot de passe incorrect."), "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/deconnexion", methods=["POST"])
def logout():
    logout_user()
    flash(_("Vous êtes déconnecté."), "info")
    return redirect(url_for("auth.login"))


@bp.route("/mot-de-passe", methods=["GET", "POST"])
@login_required
@no_store
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            form.current_password.errors.append(_("Mot de passe actuel incorrect."))
        elif form.new_password.data == form.current_password.data:
            form.new_password.errors.append(_("Choisissez un mot de passe différent de l'actuel."))
        elif form.new_password.data.lower() in {current_user.username, (current_user.matricule or "").lower()}:
            form.new_password.errors.append(_("Le mot de passe doit être différent de l'identifiant."))
        else:
            current_user.set_password(form.new_password.data)
            current_user.must_change_password = False
            db.session.commit()
            # La version de session a changé : on renouvelle la connexion de cet appareil.
            login_user(current_user._get_current_object())
            flash(_("Mot de passe modifié."), "success")
            return redirect(url_for("main.home"))
    return render_template("auth/change_password.html", form=form)


@bp.route("/inscription", methods=["GET", "POST"])
@no_store
def register():
    if not current_app.config["ALLOW_SELF_REGISTRATION"]:
        abort(404)
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegisterForm()
    form.promotion_id.choices = [
        (p.id, p.name) for p in Promotion.query.filter_by(is_active=True).order_by(Promotion.name)
    ]
    if form.validate_on_submit():
        matricule = form.matricule.data.upper()
        if User.query.filter((User.matricule == matricule) | (User.username == matricule.lower())).first():
            form.matricule.errors.append(_("Ce matricule est déjà enregistré."))
        elif form.email.data and User.query.filter_by(email=form.email.data.lower()).first():
            form.email.errors.append(_("Cet e-mail est déjà utilisé."))
        else:
            user = User(
                username=matricule.lower(),
                matricule=matricule,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data.lower() if form.email.data else None,
                promotion_id=form.promotion_id.data,
                role=ROLE_STUDENT,
                is_active=False,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(_("Demande envoyée. Vous pourrez vous connecter dès que l'administration aura validé votre compte."), "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)
