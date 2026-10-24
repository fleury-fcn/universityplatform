from flask import Blueprint

bp = Blueprint("tips", __name__, url_prefix="/tuyaux")

from . import routes  # noqa: E402,F401
