from flask import Blueprint

bp = Blueprint("schedule", __name__, url_prefix="/emploi-du-temps")

from . import routes  # noqa: E402,F401
