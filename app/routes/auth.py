

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from ..models.Users import User
from ..extensions import db, mail

authbp = Blueprint('auth', __name__)

def get_serializer():
    from .. import app
    return URLSafeTimedSerializer(app.config['SECRET_KEY'])

@authbp.route('/connexion', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('principale.Page_Principale'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Email ou mot de passe incorrect', 'danger')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=remember)
        user.update_login_time()
        flash(f'Bienvenue {user.prenom} {user.nom} !', 'success')
        return redirect(url_for('principale.Page_Principale'))
    
    return render_template('auth/login.html')

@authbp.route('/inscriptionuser', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('principale.Page_Principale'))
        
    if request.method == 'POST':
        try:
            data = {
                'username': request.form.get('username', '').strip(),
                'email': request.form.get('email', '').strip(),
                'prenom': request.form.get('prenom', '').strip(),
                'nom': request.form.get('nom', '').strip(),
                'role': request.form.get('role', 'student').strip(),
                'password': request.form.get('password', '').strip()
            }
            confirm_password = request.form.get('confirm_password', '').strip()

            # Validation
            if not all(data.values()):
                flash('Tous les champs obligatoires doivent être remplis', 'danger')
                return redirect(url_for('auth.register'))
                
            if data['password'] != confirm_password:
                flash('Les mots de passe ne correspondent pas', 'danger')
                return redirect(url_for('auth.register'))
                
            if len(data['password']) < 8:
                flash('Le mot de passe doit contenir au moins 8 caractères', 'danger')
                return redirect(url_for('auth.register'))

            # Création utilisateur avec mot de passe
            new_user = User(**data)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Compte créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('auth.login'))

        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
        except IntegrityError:
            db.session.rollback()
            flash('Un compte existe déjà avec cet email ou ce nom d\'utilisateur', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la création du compte: {str(e)}", 'danger')
        
        return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')

@authbp.route('/deconnexion')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté avec succès', 'info')
    return redirect(url_for('auth.login'))

@authbp.route('/profil', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            current_user.prenom = request.form.get('prenom', current_user.prenom).strip()
            current_user.nom = request.form.get('nom', current_user.nom).strip()
            current_user.email = request.form.get('email', current_user.email).strip()
            
            # Gestion du changement de mot de passe
            new_password = request.form.get('new_password')
            if new_password:
                if len(new_password) < 8:
                    flash('Le mot de passe doit contenir au moins 8 caractères', 'danger')
                    return redirect(url_for('auth.profile'))
                
                current_password = request.form.get('current_password')
                if not current_user.check_password(current_password):
                    flash('Mot de passe actuel incorrect', 'danger')
                    return redirect(url_for('auth.profile'))
                
                current_user.password = new_password
                flash('Mot de passe mis à jour avec succès', 'success')
            
            db.session.commit()
            flash('Profil mis à jour avec succès', 'success')
            
        except IntegrityError:
            db.session.rollback()
            flash('Cet email est déjà utilisé par un autre compte', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la mise à jour: {str(e)}", 'danger')
            
        return redirect(url_for('profilebp.profile'))
    
    return render_template('PageProfil.html')

@authbp.route('/reinitialisation-mot-de-passe', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('principale.Page_Principale'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            serializer = get_serializer()
            token = serializer.dumps(email, salt='password-reset')
            reset_url = url_for('auth.reset_password_token', token=token, _external=True)
            
            msg = Message(
                "Réinitialisation de mot de passe OpenISTA",
                sender="no-reply@openista.com",
                recipients=[email]
            )
            msg.body = f"""Pour réinitialiser votre mot de passe, cliquez sur le lien suivant :
{reset_url}

Ce lien expirera dans 1 heure.

Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email.
"""
            mail.send(msg)
        
        flash('Si un compte existe avec cet email, vous recevrez un lien de réinitialisation', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html')

@authbp.route('/reinitialisation-mot-de-passe/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('principale.Page_Principale'))
        
    try:
        serializer = get_serializer()
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except:
        flash('Lien de réinitialisation invalide ou expiré', 'danger')
        return redirect(url_for('auth.reset_password_request'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Utilisateur introuvable', 'danger')
        return redirect(url_for('auth.reset_password_request'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'danger')
        elif len(password) < 8:
            flash('Le mot de passe doit contenir au moins 8 caractères', 'danger')
        else:
            user.password = password
            db.session.commit()
            flash('Mot de passe mis à jour avec succès', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)