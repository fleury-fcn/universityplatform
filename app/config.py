"""Configuration de l'application, lue uniquement depuis l'environnement."""
import os
import secrets
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"

load_dotenv(BASE_DIR / ".env")


def _bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "oui"}


def _database_url():
    url = os.environ.get("DATABASE_URL") or f"sqlite:///{(INSTANCE_DIR / 'ista.sqlite').as_posix()}"
    # Les hébergeurs (Render, Heroku...) fournissent souvent "postgres://".
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or str(INSTANCE_DIR / "uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_MB", "10")) * 1024 * 1024

    # À incrémenter à chaque livraison pour invalider les caches (navigateur et hors ligne).
    ASSET_VERSION = "1"

    LANGUAGES = {"fr": "Français", "en": "English", "rn": "Ikirundi"}
    BABEL_DEFAULT_LOCALE = "fr"
    BABEL_DEFAULT_TIMEZONE = os.environ.get("APP_TIMEZONE", "Africa/Bujumbura")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    # Les étudiants utilisent surtout leur téléphone : session longue si "se souvenir de moi".
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    WTF_CSRF_TIME_LIMIT = None

    ALLOW_SELF_REGISTRATION = _bool("ALLOW_SELF_REGISTRATION", False)
    # Note minimale (sur 20) pour valider un cours. À confirmer par l'ISTA.
    PASS_MARK = float(os.environ.get("PASS_MARK", "10"))

    @classmethod
    def init_app(cls, app):
        pass


class DevelopmentConfig(Config):
    DEBUG = _bool("FLASK_DEBUG", True)

    @classmethod
    def init_app(cls, app):
        if not app.config.get("SECRET_KEY"):
            app.config["SECRET_KEY"] = secrets.token_hex(32)
            app.logger.warning("SECRET_KEY absente : clé temporaire générée (développement uniquement).")


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "cle-de-test-uniquement"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = _bool("COOKIE_SECURE", True)
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE

    @classmethod
    def init_app(cls, app):
        if not app.config.get("SECRET_KEY"):
            raise RuntimeError("SECRET_KEY doit être définie en production.")


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
