"""Dates locales (fuseau de l'institut, Africa/Bujumbura par défaut)."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

from flask import current_app


def local_now():
    return datetime.now(ZoneInfo(current_app.config["BABEL_DEFAULT_TIMEZONE"]))


def local_today():
    return local_now().date()


def parse_date(value, default=None):
    try:
        return date.fromisoformat(value) if value else default
    except ValueError:
        return default
