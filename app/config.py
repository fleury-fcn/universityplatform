
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

class Config:
    # Configuration de base
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'votre-cle-secure-par-defaut-123!'
    
    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://fleury:NouveauMotDePasse123!@127.0.0.1/OpenIsta?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600
    }


    # Configuration Flask-Mail (pour la réinitialisation de mot de passe)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'votre.email@openista.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'votre-mot-de-passe-email'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'no-reply@openista.com'

    # Configuration des tokens
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'un-sel-securise-pour-les-tokens'

    # Configuration des sessions
    PERMANENT_SESSION_LIFETIME = 3600  # 1 heure en secondes

    # Mode debug
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Affiche les requêtes SQL dans la console


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    # Désactive le mode debug pour la production
    DEBUG = False
    
    # Configuration plus stricte pour la production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


# Configuration par défaut
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

