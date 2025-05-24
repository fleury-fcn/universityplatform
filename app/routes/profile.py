from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user, logout_user
from werkzeug.utils import secure_filename
import os
from ..models.Users import User
from ..extensions import db
from datetime import datetime

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

profilebp = Blueprint('profile', __name__)

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profilebp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Configuration des uploads
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    current_app.config['UPLOAD_FOLDER'] = upload_folder
    current_app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
    
    # Créer le dossier uploads s'il n'existe pas
    os.makedirs(upload_folder, exist_ok=True)

    if request.method == 'POST':
        # Gestion de la désactivation de compte
        if 'delete_account' in request.form:
            current_password = request.form.get('current_password')
            
            if not current_user.check_password(current_password):
                flash('Mot de passe incorrect', 'danger')
                return redirect(url_for('profile.profile'))
            
            try:
                # 1. Anonymiser les données sensibles
                current_user.email = f"deleted_{current_user.id}@example.com"
                current_user.username = f"deleted_user_{current_user.id}"
                current_user.password_hash = ""  # Invalider le mot de passe
                
                # 2. Supprimer l'avatar si existe
                current_user.delete_avatar()
                
                # 3. Marquer le compte comme désactivé
                current_user.is_active = False
                current_user.deleted_at = datetime.utcnow()
                
                db.session.commit()
                
                logout_user()
                flash('Votre compte a été désactivé avec succès', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Erreur désactivation compte: {str(e)}")
                flash('Erreur lors de la désactivation du compte', 'danger')
                return redirect(url_for('profile.profile'))

        # Gestion de la mise à jour du profil
        prenom = request.form.get('prenom', current_user.prenom)
        nom = request.form.get('nom', current_user.nom)
        email = request.form.get('email', current_user.email)
        
        # Validation des champs obligatoires
        if not email:
            flash('L\'email est obligatoire', 'danger')
            return redirect(url_for('profile.profile'))
        
        # Mise à jour des informations de base
        current_user.prenom = prenom
        current_user.nom = nom
        current_user.email = email
        current_user.updated_at = datetime.utcnow()
        
        # Gestion du mot de passe si fourni
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        current_password = request.form.get('current_password')
        
        if new_password:
            if new_password != confirm_password:
                flash('Les nouveaux mots de passe ne correspondent pas.', 'danger')
                return redirect(url_for('profile.profile'))
            
            if not current_user.check_password(current_password):
                flash('Mot de passe actuel incorrect.', 'danger')
                return redirect(url_for('profile.profile'))
            
            current_user.set_password(new_password)
        
        # Gestion de l'avatar
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename and allowed_file(file.filename):
                if file.content_length > MAX_FILE_SIZE:
                    flash('Fichier trop volumineux (max 2MB)', 'danger')
                else:
                    try:
                        # Supprimer l'ancien avatar
                        current_user.delete_avatar()
                        
                        # Sauvegarder le nouveau
                        ext = file.filename.rsplit('.', 1)[1].lower()
                        filename = f"user_{current_user.id}_{int(datetime.now().timestamp())}.{ext}"
                        filepath = os.path.join(upload_folder, filename)
                        
                        file.save(filepath)
                        current_user.avatar = filename
                    except Exception as e:
                        current_app.logger.error(f"Erreur upload avatar: {str(e)}")
                        flash("Erreur lors de l'enregistrement de l'avatar", "danger")

        try:
            db.session.commit()
            flash('Votre profil a été mis à jour avec succès.', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur mise à jour profil: {str(e)}")
            flash('Une erreur est survenue lors de la mise à jour du profil.', 'danger')
        
        return redirect(url_for('profile.profile'))
    
    return render_template('PageProfil.html')