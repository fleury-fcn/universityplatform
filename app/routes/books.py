from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, send_from_directory, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
import os
from datetime import datetime
from ..models.books import Book, BookDownload
from ..models.Users import User

# Constants
ADMIN_ROLES = ['administrateur', 'admin']
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'epub'}
MAX_DAILY_DOWNLOADS = 3

# Create Blueprint
books_bp = Blueprint('books', __name__, url_prefix='/bibliotheque')

# Configure upload folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS_FOLDER = os.path.join(BASE_DIR, 'static', 'books')

# Ensure upload folder exists
os.makedirs(BOOKS_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@books_bp.route('/')
@login_required
def library():
    try:
        # Get all books ordered by upload date (descending)
        books = Book.query.order_by(Book.upload_date.desc()).all()
        
        # Get distinct categories for filtering
        categories = [cat[0] for cat in db.session.query(Book.category.distinct()).all()]
        
        current_date = datetime.now().strftime("%d/%m/%Y")
        
        return render_template('books/PageLivres.html', 
                            books=books,
                            categories=categories,
                            current_date=current_date,
                            current_user=current_user)
    
    except Exception as e:
        current_app.logger.error(f"Error in library route: {str(e)}")
        flash("An error occurred while loading the library", "danger")
        return redirect(url_for('main.Page_Accueil'))

@books_bp.route('/details/<int:book_id>')
@login_required
def book_details(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        today = datetime.utcnow().date()
        
        # Vérifier les téléchargements de l'utilisateur aujourd'hui
        download_record = BookDownload.query.filter_by(
            user_id=current_user.id,
            book_id=book_id,  # Ajout important!
            download_date=today
        ).first()

        # Préparer toutes les données nécessaires pour le template
        template_data = {
            'book': book,
            'can_download': not download_record or download_record.download_count < 3,
            'downloads_today': download_record.download_count if download_record else 0,
            'current_user': current_user,
           
        }
        
        return render_template('books/book_details.html', **template_data)
    
    except Exception as e:
        current_app.logger.error(f"Erreur dans book_details: {str(e)}")
        flash("Une erreur est survenue lors du chargement des détails", "danger")
        return redirect(url_for('books.library'))
    

    
@books_bp.route('/download/<int:book_id>')
@login_required
def download_book(book_id):
    try:
        today = datetime.utcnow().date()
        book = Book.query.get_or_404(book_id)
        
        # Check download limit
        download_record = BookDownload.query.filter_by(
            user_id=current_user.id,
            download_date=today
        ).first()
        
        if download_record and download_record.download_count >= MAX_DAILY_DOWNLOADS:
            flash(f'You have reached your daily download limit of {MAX_DAILY_DOWNLOADS}', 'warning')
            return redirect(url_for('books.book_details', book_id=book_id))
        
        # Verify file exists
        file_path = os.path.join(BOOKS_FOLDER, book.file_path)
        if not os.path.exists(file_path):
            flash("The requested file does not exist on the server", "danger")
            return redirect(url_for('books.library'))
            
        # Record the download
        if download_record:
            download_record.download_count += 1
        else:
            download_record = BookDownload(
                user_id=current_user.id,
                book_id=book_id,
                download_count=1,
                download_date=today
            )
            db.session.add(download_record)
        
        # Update book download count
        book.downloads += 1
        db.session.commit()
        
        # Send file with clean filename
        original_filename = f"{secure_filename(book.title)}.{book.file_type}"
        return send_from_directory(
            directory=BOOKS_FOLDER,
            path=book.file_path,
            as_attachment=True,
            download_name=original_filename
        )
    
    except Exception as e:
        current_app.logger.error(f"Error in download_book: {str(e)}")
        flash("An error occurred during download", "danger")
        return redirect(url_for('books.library'))

@books_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_book():
    # Vérification des permissions
    if not current_user.is_authenticated or current_user.role != 'administrateur':
        flash('Accès réservé aux administrateurs', 'danger')
        return redirect(url_for('books.library'))

    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            title = request.form.get('title', '').strip()
            author = request.form.get('author', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', '').strip()
            language = request.form.get('language', '').strip()
            level = request.form.get('level', '').strip()

            # Validation des champs requis
            if not all([title, author, category, language, level]):
                flash('Veuillez remplir tous les champs obligatoires', 'danger')
                return render_template('books/add_book.html',
                                    form_data=request.form,
                                    categories=CATEGORIES,
                                    languages=LANGUAGES,
                                    levels=LEVELS)

            # Vérification du fichier
            if 'file' not in request.files:
                flash('Aucun fichier sélectionné', 'danger')
                return render_template('books/add_book.html',
                                    form_data=request.form,
                                    categories=CATEGORIES,
                                    languages=LANGUAGES,
                                    levels=LEVELS)

            file = request.files['file']
            if file.filename == '':
                flash('Aucun fichier sélectionné', 'danger')
                return render_template('books/add_book.html',
                                    form_data=request.form,
                                    categories=CATEGORIES,
                                    languages=LANGUAGES,
                                    levels=LEVELS)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(BOOKS_FOLDER, unique_filename)
                
                # Sauvegarde du fichier
                file.save(file_path)
                
                # Vérification que le fichier a bien été sauvegardé
                if not os.path.exists(file_path):
                    flash("Erreur lors de l'enregistrement du fichier", 'danger')
                    return render_template('books/add_book.html',
                                        form_data=request.form,
                                        categories=CATEGORIES,
                                        languages=LANGUAGES,
                                        levels=LEVELS)

                # Création du livre
                new_book = Book(
                    title=title,
                    author=author,
                    description=description,
                    category=category,
                    language=language,
                    level=level,
                    file_path=unique_filename,
                    file_size=os.path.getsize(file_path) // 1024,  # Taille en KB
                    file_type=filename.rsplit('.', 1)[1].lower(),
                    user_id=current_user.id
                )

                db.session.add(new_book)
                db.session.commit()

                flash('Livre ajouté avec succès!', 'success')
                return redirect(url_for('books.library'))
            else:
                flash('Format de fichier non autorisé', 'danger')

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur dans add_book: {str(e)}")
            flash("Une erreur est survenue lors de l'ajout du livre", "danger")

    # Constantes pour les sélecteurs
    CATEGORIES = ['statistique', 'probabilite', 'actuariat', 'data-science', 'informatique', 'divers']
    LANGUAGES = ['fr', 'en', 'ar']
    LEVELS = ['bac', 'master', 'doctorat']

    return render_template('books/add_book.html',
                         form_data=None,
                         categories=CATEGORIES,
                         languages=LANGUAGES,
                         levels=LEVELS)

@books_bp.route('/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if not current_user.is_authenticated or current_user.role != 'administrateur':
        flash('Accès réservé aux administrateurs', 'danger')
        return redirect(url_for('books.library'))

    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        try:
            # Mise à jour des métadonnées
            book.title = request.form.get('title', book.title)
            book.author = request.form.get('author', book.author)
            book.description = request.form.get('description', book.description)
            book.category = request.form.get('category', book.category)
            book.language = request.form.get('language', book.language)
            book.level = request.form.get('level', book.level)
            
            # Gestion du fichier
            if 'file' in request.files:
                file = request.files['file']
                if file.filename != '' and allowed_file(file.filename):
                    # Supprimer l'ancien fichier
                    if book.file_path:
                        try:
                            os.remove(os.path.join(BOOKS_FOLDER, book.file_path))
                        except OSError:
                            pass
                    
                    # Sauvegarder le nouveau fichier
                    filename = secure_filename(file.filename)
                    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                    file.save(os.path.join(BOOKS_FOLDER, unique_filename))
                    
                    book.file_path = unique_filename
                    book.file_size = os.path.getsize(os.path.join(BOOKS_FOLDER, unique_filename)) // 1024
                    book.file_type = filename.rsplit('.', 1)[1].lower()
            
            db.session.commit()
            flash('Livre mis à jour avec succès', 'success')
            return redirect(url_for('books.book_details', book_id=book.id))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur dans edit_book: {str(e)}")
            flash("Une erreur est survenue lors de la modification", "danger")
    
    # Préparer les données pour le template
    categories = ['statistique', 'probabilite', 'actuariat', 'data-science', 'informatique', 'divers']
    languages = ['fr', 'en', 'ar']
    levels = ['bac', 'master', 'doctorat']
    
    return render_template('books/edit_book.html',
                         book=book,
                         categories=categories,
                         languages=languages,
                         levels=levels,
                         form=request.form)  # Ajout de la variable form

@books_bp.route('/delete/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    try:
        # Vérification renforcée des permissions
        if not current_user.is_authenticated or current_user.role.lower() != 'administrateur':
            flash('Action non autorisée', 'danger')
            return redirect(url_for('books.library'))

        book = Book.query.get_or_404(book_id)
        
        # Suppression du fichier physique
        if book.file_path:
            try:
                file_path = os.path.join(current_app.config['BOOKS_FOLDER'], book.file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                current_app.logger.error(f"Erreur suppression fichier: {str(e)}")
                flash("Erreur lors de la suppression du fichier", "warning")

        # Suppression des téléchargements associés
        BookDownload.query.filter_by(book_id=book_id).delete()
        
        # Suppression du livre
        db.session.delete(book)
        db.session.commit()
        
        flash('Livre supprimé avec succès', 'success')
        return redirect(url_for('books.library'))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur suppression livre: {str(e)}")
        flash("Erreur lors de la suppression du livre", "danger")
        return redirect(url_for('books.library'))