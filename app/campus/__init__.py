from flask import Blueprint

bp = Blueprint("campus", __name__, url_prefix="/campus")

from . import routes  # noqa: E402,F401
