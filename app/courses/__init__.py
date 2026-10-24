from flask import Blueprint

bp = Blueprint("courses", __name__, url_prefix="/cours")

from . import routes  # noqa: E402,F401
