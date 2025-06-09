from flask import Flask
from flask_migrate import Migrate
from .extensions import db, login_manager, mail
import os
from .context_processors import register_context_processors
from dotenv import load_dotenv  

load_dotenv()  # Charge les variables d'environnement

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    register_context_processors(app)
    app.secret_key = 'votre_cle_secrete'

    # Configuration MySQL avec variables d'environnement
    app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_HOST', '127.0.0.1')
    app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_USER', 'fleury')
    app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'NouveauMotDePasse123!')
    app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE', 'OpenIsta')
    
    # Configuration SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{app.config['MYSQL_DATABASE_USER']}:"
        f"{app.config['MYSQL_DATABASE_PASSWORD']}@"
        f"{app.config['MYSQL_DATABASE_HOST']}/"
        f"{app.config['MYSQL_DATABASE_DB']}"
    )

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
    
    # Configuration des uploads
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'messages')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    


    return app
'''

from flask import Flask
from flask_migrate import Migrate
from .extensions import db, login_manager, mail
import os
from .context_processors import register_context_processors
from dotenv import load_dotenv

load_dotenv()  # Charge les variables d'environnement

migrate = Migrate()


def create_app(config_name=None):
    app = Flask(__name__)
    
    # Charger la configuration appropriée
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Importer et appliquer la configuration
    from .config import config
    app.config.from_object(config[config_name])
    
    # Enregistrer les context processors
    register_context_processors(app)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Flask-Login Configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page"
    login_manager.login_message_category = 'info'

    # Register Blueprints
    from app.routes import all_blueprints
    for bp in all_blueprints:
        app.register_blueprint(bp)

    # User loader for Flask-Login
    from app.models.Users import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Configuration des uploads
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'messages')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Créer les tables si elles n'existent pas (en mode développement)
    if config_name == 'development':
        with app.app_context():
            try:
                db.create_all()
                print("✅ Tables de base de données créées avec succès!")
            except Exception as e:
                print(f"⚠️ Erreur lors de la création des tables: {e}")

    return app '''
