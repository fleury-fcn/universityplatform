from flask import Blueprint

bp = Blueprint("grades", __name__, url_prefix="/notes")

from . import routes  # noqa: E402,F401
