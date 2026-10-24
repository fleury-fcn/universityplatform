from flask import Blueprint

bp = Blueprint("faq", __name__, url_prefix="/faq")

from . import routes  # noqa: E402,F401
