'''from flask_sqlalchemy import SQLAlchemy

# Initialiser SQLAlchemy une extension que nous utilisons pour gere une base des donnes 
db = SQLAlchemy()'''


from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()  