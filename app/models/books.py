'''from datetime import datetime
from app.extensions import db
from flask_login import UserMixin



class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # statistique, probabilite, etc.
    language = db.Column(db.String(20), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # bac, master, doctorat
    file_path = db.Column(db.String(255), nullable=False)  # Chemin vers le fichier
    file_size = db.Column(db.Integer)  # Taille en KB
    file_type = db.Column(db.String(20))  # pdf, docx, etc.
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    downloads = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    title = db.Column(db.String(200))
    disponible = db.Column(db.Boolean, default=True)

class BookDownload(db.Model):
    __tablename__ = 'book_downloads'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    download_date = db.Column(db.Date, default=datetime.utcnow().date())
    download_count = db.Column(db.Integer, default=0)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', 'download_date', name='unique_user_book_day'),
    )'''

from datetime import datetime
from app.extensions import db

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(20), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(20))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    downloads = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'))
    disponible = db.Column(db.Boolean, default=True)

class BookDownload(db.Model):
    __tablename__ = 'book_downloads'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateurs.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    download_date = db.Column(db.Date, default=datetime.utcnow().date())
    download_count = db.Column(db.Integer, default=0)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', 'download_date', name='unique_user_book_day'),
    )