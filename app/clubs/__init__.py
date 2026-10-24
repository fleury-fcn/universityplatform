from flask import Blueprint

bp = Blueprint("clubs", __name__, url_prefix="/clubs")

from . import routes  # noqa: E402,F401
