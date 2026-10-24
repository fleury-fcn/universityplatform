from flask import Blueprint

bp = Blueprint("admin", __name__, url_prefix="/admin")

from . import academic, routes  # noqa: E402,F401
