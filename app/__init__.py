"""Application étudiante de l'Institut de Statistique Appliquée (ISTA)."""
import os
from importlib import import_module

from flask import Flask, render_template, request
from flask_login import current_user

from .config import INSTANCE_DIR, config_by_name
from .extensions import babel, csrf, db, login_manager, migrate

# Chaque module expose un Blueprint nommé "bp".
BLUEPRINTS = [
    "app.main",
    "app.auth",
    "app.profile",
    "app.admin",
    "app.notifications",
    "app.news",
    "app.schedule",
    "app.files",
    "app.courses",
    "app.grades",
    "app.library",
    "app.campus",
    "app.clubs",
    "app.tips",
    "app.messages",
]


def select_locale():
    from flask import current_app

    languages = current_app.config["LANGUAGES"]
    lang = request.cookies.get("lang")
    if lang in languages:
        return lang
    user_lang = getattr(current_user, "locale", None) if current_user else None
    if user_lang in languages:
        return user_lang
    return current_app.config["BABEL_DEFAULT_LOCALE"]


def create_app(config_name=None):
    config_name = config_name or os.environ.get("APP_ENV", "development")
    cfg = config_by_name[config_name]
    app = Flask(__name__, instance_path=str(INSTANCE_DIR))
    app.config.from_object(cfg)
    cfg.init_app(app)

    if app.config["TRUST_PROXY"]:
        from werkzeug.middleware.proxy_fix import ProxyFix

        n = app.config["TRUST_PROXY"]
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=n, x_proto=n, x_host=n)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True, compare_type=True)
    login_manager.init_app(app)
    csrf.init_app(app)
    babel.init_app(app, locale_selector=select_locale)

    login_manager.login_view = "auth.login"
    login_manager.login_message = None
    login_manager.session_protection = "strong"

    from .core.i18n import compile_catalogs

    compile_catalogs(os.path.join(app.root_path, "translations"))

    from . import models  # noqa: F401  (enregistre les modèles auprès de SQLAlchemy)
    from .core import security, templating

    security.init_app(app)
    templating.init_app(app)

    from .services import push

    push.init_app(app)

    for path in BLUEPRINTS:
        app.register_blueprint(import_module(path).bp)

    @login_manager.user_loader
    def load_user(session_id):
        from .models import User

        try:
            user_id, version = (int(part) for part in session_id.split(":"))
        except ValueError:
            return None
        user = db.session.get(User, user_id)
        if user is None or not user.is_active or user.session_version != version:
            return None
        return user

    from .cli import register_cli

    register_cli(app)
    _register_error_handlers(app)
    return app


def _register_error_handlers(app):
    def render_error(code):
        return render_template("errors.html", code=code), code

    for code in (400, 403, 404, 413, 500):
        app.register_error_handler(code, lambda e, code=code: render_error(code))
