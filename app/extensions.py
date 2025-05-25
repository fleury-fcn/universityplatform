from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail  # Cette ligne est cruciale

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()  # Cette initialisation doit être présente