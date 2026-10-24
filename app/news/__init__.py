from flask import Blueprint

bp = Blueprint("news", __name__, url_prefix="/actualites")

from . import routes  # noqa: E402,F401
