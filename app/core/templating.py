"""Variables et filtres communs à tous les gabarits."""
from flask import current_app
from flask_babel import format_date, format_datetime, get_locale
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from markupsafe import Markup, escape

from .security import ROLE_ADMIN

# Fonctionnalités affichées sur l'accueil. Une entrée n'apparaît que si sa vue existe.
FEATURES = [
    {"endpoint": "news.index", "label": _l("Actualités"), "icon": "news"},
    {"endpoint": "schedule.index", "label": _l("Emploi du temps"), "icon": "calendar"},
    {"endpoint": "courses.index", "label": _l("Cours"), "icon": "book"},
    {"endpoint": "grades.index", "label": _l("Notes"), "icon": "chart"},
    {"endpoint": "library.index", "label": _l("Bibliothèque"), "icon": "library"},
    {"endpoint": "campus.index", "label": _l("Campus"), "icon": "map"},
    {"endpoint": "clubs.index", "label": _l("Clubs"), "icon": "users"},
    {"endpoint": "tips.index", "label": _l("Tuyaux"), "icon": "bulb"},
    {"endpoint": "messages.inbox", "label": _l("Messages"), "icon": "mail"},
    {"endpoint": "faq.index", "label": _l("Questions fréquentes"), "icon": "help"},
    {"endpoint": "admin.index", "label": _l("Administration"), "icon": "settings", "roles": {ROLE_ADMIN}},
]

NAV = [
    {"endpoint": "main.home", "label": _l("Accueil"), "icon": "home"},
    {"endpoint": "schedule.index", "label": _l("Horaires"), "icon": "calendar"},
    {"endpoint": "courses.index", "label": _l("Cours"), "icon": "book"},
    {"endpoint": "notifications.index", "label": _l("Alertes"), "icon": "bell"},
    {"endpoint": "profile.show", "label": _l("Profil"), "icon": "user"},
]


def _visible(items):
    views = current_app.view_functions
    role = getattr(current_user, "role", None)
    return [i for i in items if i["endpoint"] in views and (not i.get("roles") or role in i["roles"])]


def text_to_html(value):
    """Affiche un texte saisi par un utilisateur : échappé, paragraphes et retours à la ligne."""
    if not value:
        return ""
    paragraphs = escape(value.strip()).split("\n\n")
    return Markup("".join(f"<p>{p}</p>" for p in paragraphs).replace("\n", Markup("<br>")))


def init_app(app):
    app.jinja_env.filters.update(
        date=lambda v, fmt="medium": format_date(v, fmt) if v else "",
        datetime=lambda v, fmt="short": format_datetime(v, fmt) if v else "",
        time=lambda v: v.strftime("%H:%M") if v else "",
        text=text_to_html,
    )

    @app.context_processor
    def inject_globals():
        return {
            "features": _visible(FEATURES),
            "nav_items": _visible(NAV),
            "languages": current_app.config["LANGUAGES"],
            "current_locale": str(get_locale()),
            "has_view": lambda endpoint: endpoint in current_app.view_functions,
        }
