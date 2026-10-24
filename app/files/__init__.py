from flask import Blueprint

bp = Blueprint("files", __name__, url_prefix="/fichiers")

from . import routes  # noqa: E402,F401
