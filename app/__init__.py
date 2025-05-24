
from flask import Flask
from flask_migrate import Migrate
from .extensions import db, login_manager, mail
import os

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # MySQL Configuration
    app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
    app.config['MYSQL_DATABASE_USER'] = 'fleury'
    app.config['MYSQL_DATABASE_PASSWORD'] = 'NouveauMotDePasse123!'
    app.config['MYSQL_DATABASE_DB'] = 'OpenIsta'

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Flask-Login Configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page"

    # Register Blueprints
    from app.routes import all_blueprints
    for bp in all_blueprints:
        app.register_blueprint(bp)

    # User loader for Flask-Login
    from app.models.Users import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'messages')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app

    