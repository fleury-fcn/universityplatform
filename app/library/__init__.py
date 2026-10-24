from flask import Blueprint

bp = Blueprint("library", __name__, url_prefix="/bibliotheque")

from . import routes  # noqa: E402,F401
