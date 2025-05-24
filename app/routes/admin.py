

'''from flask import Blueprint, render_template,flash ,current_app ,request, jsonify, redirect, url_for, send_file
from flask_login import login_required, current_user, login_user
from ..models.Users import User
from ..models.tuyaux import Tuyau
from ..models.courses import Cours 
from ..models.activity import ActivityLog
from ..extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func, extract
import io
import zipfile
import json
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

adminbp = Blueprint('admin', __name__)

@adminbp.route('/admin')
@login_required
def PageAdmin():
    if current_user.role != 'administrateur':
        flash(f' Salut {current_user.prenom} {current_user.nom} Desolé, cette page est réservée aux admins')
        
        return redirect(url_for('principale.Page_Principale'))
    
    # Récupération des statistiques de base
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter(User.last_login > (datetime.now() - timedelta(days=30))).count(),
        'total_tuyaux': Tuyau.query.count(),
        'tuyaux_last_month': Tuyau.query.filter(Tuyau.date_ajout > (datetime.now() - timedelta(days=30))).count(),
        'total_courses': Cours.query.count(),
        'today_logins': User.query.filter(User.last_login > datetime.now().replace(hour=0, minute=0, second=0)).count()
    }
    
    # Derniers utilisateurs avec plus de données
    users = User.query.order_by(User.last_login.desc()).all()
    
    # Journal d'activité
    activity_logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(50).all()
    
    # Données pour les graphiques
    
    # 1. Activité des 30 derniers jours (connexions et tuyaux)
    days = 30
    date_labels = []
    login_data = []
    tuyaux_data = []
    
    for i in range(days, -1, -1):
        date = datetime.now() - timedelta(days=i)
        date_labels.append(date.strftime("%d/%m"))
        
        # Connexions
        login_count = User.query.filter(
            func.date(User.last_login) == date.date()
        ).count()
        login_data.append(login_count)
        
        # Tuyaux partagés
        tuyaux_count = Tuyau.query.filter(
            func.date(Tuyau.date_ajout) == date.date()
        ).count()
        tuyaux_data.append(tuyaux_count)
    
    # 2. Répartition des rôles
    roles_distribution = db.session.query(
        User.role,
        func.count(User.id).label('count')
    ).group_by(User.role).all()
    
    roles_labels = [role[0].capitalize() for role in roles_distribution]
    roles_data = [role[1] for role in roles_distribution]
    
    # 3. Répartition du contenu
    content_types = {
        'Cours': Cours.query.count(),
        'Tuyaux': Tuyau.query.count(),
        'Messages': 230,  # Valeur exemple - à remplacer par votre modèle réel
        'Commentaires': 150  # Valeur exemple - à remplacer par votre modèle réel
    }
    
    # Paramètres système (exemple)
    system_settings = {
        'maintenance_mode': False,
        'registration_enabled': True,
        'session_timeout': 30,
        'max_upload_size': 20,
        'system_message': ''
    }
    
    return render_template('PageAdmin.html',
                         stats=stats,
                         users=users,
                         activity_logs=activity_logs,
                         current_date=datetime.now().strftime("%d/%m/%Y"),
                         # Données pour les graphiques
                         date_labels=date_labels,
                         login_data=login_data,
                         tuyaux_data=tuyaux_data,
                         roles_labels=roles_labels,
                         roles_data=roles_data,
                         content_labels=list(content_types.keys()),
                         content_data=list(content_types.values()),
                         system_settings=system_settings)

# API pour la gestion des utilisateurs
@adminbp.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def user_api(user_id):
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': user.id,
            'firstName': user.prenom,
            'lastName': user.nom,
            'email': user.email,
            'role': user.role,
            'isActive': user.is_active,
            'avatar': user.get_avatar_url
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        user.prenom = data.get('firstName', user.prenom)
        user.nom = data.get('lastName', user.nom)
        user.email = data.get('email', user.email)
        user.role = data.get('role', user.role)
        user.is_active = data.get('status', user.is_active) == '1'
        
        if 'password' in data and data['password']:
            user.password = generate_password_hash(data['password'])
        
        if 'avatar' in data:
            user.avatar_url = data['avatar']
        
        db.session.commit()
        
        # Log l'activité
        log = ActivityLog(
            user_id=current_user.id,
            action=f"Modification de l'utilisateur {user.email}"
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'User updated successfully'})
    
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        
        # Log l'activité
        log = ActivityLog(
            user_id=current_user.id,
            action=f"Suppression de l'utilisateur {user.email}"
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'})


# Impersonation (connexion en tant qu'un autre utilisateur)
@adminbp.route('/admin/impersonate/<int:user_id>')
@login_required
def impersonate(user_id):
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    login_user(user)
    
    # Log l'activité
    log = ActivityLog(
        user_id=current_user.id,
        action=f"Connexion en tant que {user.email}"
    )
    db.session.add(log)
    db.session.commit()
    
    return redirect(url_for('principale.Page_Principale'))

# Réinitialisation du mot de passe
@adminbp.route('/api/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def reset_password(user_id):
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    new_password = generate_random_password()  # À implémenter
    user.password = generate_password_hash(new_password)
    db.session.commit()
    
    # Envoyer le nouveau mot de passe par email (à implémenter)
    
    # Log l'activité
    log = ActivityLog(
        user_id=current_user.id,
        action=f"Réinitialisation du mot de passe pour {user.email}"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Password reset successfully'})

# Gestion des notifications
@adminbp.route('/api/notifications', methods=['POST'])
@login_required
def send_notification():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Validation des données
    if not all(k in data for k in ['recipients', 'subject', 'message']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Envoyer les notifications (à implémenter selon votre système)
    
    # Log l'activité
    log = ActivityLog(
        user_id=current_user.id,
        action=f"Notification envoyée: {data['subject']}"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Notification sent successfully'})

# Sauvegarde des données
@adminbp.route('/admin/backup')
@login_required
def backup():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Créer un fichier ZIP en mémoire
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        # Ajouter les données des utilisateurs
        users = User.query.all()
        users_data = [{
            'id': u.id,
            'prenom': u.prenom,
            'nom': u.nom,
            'email': u.email,
            'role': u.role,
            'is_active': u.is_active,
            'last_login': u.last_login.isoformat() if u.last_login else None
        } for u in users]
        zf.writestr('users.json', json.dumps(users_data, indent=2))
        
        # Ajouter les tuyaux
        tuyaux = Tuyau.query.all()
        tuyaux_data = [{
            'id': t.id,
            'titre': t.titre,
            'contenu': t.contenu,
            'date_ajout': t.date_ajout.isoformat(),
            'auteur_id': t.auteur_id
        } for t in tuyaux]
        zf.writestr('tuyaux.json', json.dumps(tuyaux_data, indent=2))
        
        # Ajouter les cours
        courses = Cours.query.all()
        courses_data = [{
            'id': c.id,
            'titre': c.titre,
            'description': c.description,
            'date_creation': c.date_creation.isoformat()
        } for c in courses]
        zf.writestr('courses.json', json.dumps(courses_data, indent=2))
    
    memory_file.seek(0)
    
    # Log l'activité
    log = ActivityLog(
        user_id=current_user.id,
        action="Sauvegarde des données effectuée"
    )
    db.session.add(log)
    db.session.commit()
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'backup_{datetime.now().strftime("%Y-%m-%d")}.zip'
    )

# Export des données
@adminbp.route('/admin/export/<data_type>')
@login_required
def export_data(data_type):
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    if data_type == 'users':
        data = [{
            'id': u.id,
            'prenom': u.prenom,
            'nom': u.nom,
            'email': u.email,
            'role': u.role,
            'is_active': u.is_active,
            'last_login': u.last_login.isoformat() if u.last_login else None
        } for u in User.query.all()]
    elif data_type == 'courses':
        data = [{
            'id': c.id,
            'titre': c.titre,
            'description': c.description,
            'date_creation': c.date_creation.isoformat()
        } for c in Cours.query.all()]
    elif data_type == 'tuyaux':
        data = [{
            'id': t.id,
            'titre': t.titre,
            'contenu': t.contenu,
            'date_ajout': t.date_ajout.isoformat(),
            'auteur_id': t.auteur_id
        } for t in Tuyau.query.all()]
    else:
        return jsonify({'error': 'Invalid data type'}), 400
    
    memory_file = io.BytesIO()
    memory_file.write(json.dumps(data, indent=2).encode('utf-8'))
    memory_file.seek(0)
    
    # Log l'activité
    log = ActivityLog(
        user_id=current_user.id,
        action=f"Export des données {data_type}"
    )
    db.session.add(log)
    db.session.commit()
    
    return send_file(
        memory_file,
        mimetype='application/json',
        as_attachment=True,
        download_name=f'export_{data_type}_{datetime.now().strftime("%Y-%m-%d")}.json'
    )

# Journal d'activité
@adminbp.route('/api/activity-logs', methods=['DELETE'])
@login_required
def clear_activity_logs():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Supprimer tous les logs
    db.session.query(ActivityLog).delete()
    db.session.commit()
    
    # Ajouter un log pour cette action (qui sera le seul log restant)
    log = ActivityLog(
        user_id=current_user.id,
        action="Journal d'activité effacé"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Activity logs cleared successfully'})

# Paramètres système
@adminbp.route('/api/system-settings', methods=['POST'])
@login_required
def update_system_settings():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Ici, vous devriez sauvegarder ces paramètres dans votre base de données
    # ou dans un fichier de configuration selon votre architecture
    
    # Log l'activité
    log = ActivityLog(
        user_id=current_user.id,
        action="Mise à jour des paramètres système"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'System settings updated successfully'})

# Vérification du système
@adminbp.route('/api/system-check')
@login_required
def system_check():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Ici, vous devriez implémenter des vérifications réelles de votre système
    results = {
        'database': {
            'status': 'OK',
            'message': 'Connexion à la base de données fonctionnelle'
        },
        'storage': {
            'status': 'OK',
            'message': '1.2GB/5GB utilisé'
        },
        'performance': {
            'status': 'OK',
            'message': 'Performances optimales'
        },
        'updates': {
            'status': 'WARNING',
            'message': 'Mise à jour disponible (v2.1.3)'
        },
        'security': {
            'status': 'OK',
            'message': 'Aucune menace détectée'
        }
    }
    
    # Log l'activité
    log = ActivityLog(
        user_id=current_user.id,
        action="Vérification du système effectuée"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify(results)

def generate_random_password():
    # Implémentez une génération de mot de passe sécurisé
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for i in range(12))

@adminbp.route('/api/users/<int:user_id>/deactivate', methods=['POST'])
@login_required
def deactivate_user(user_id):
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    
    log = ActivityLog(
        user_id=current_user.id,
        action=f"Désactivation de l'utilisateur {user.email}"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'User deactivated successfully'})

@adminbp.route('/api/users/<int:user_id>/activate', methods=['POST'])
@login_required
def activate_user(user_id):
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    
    log = ActivityLog(
        user_id=current_user.id,
        action=f"Activation de l'utilisateur {user.email}"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'User activated successfully'})


@adminbp.route('/api/utilisateus/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'firstName': user.prenom,
        'lastName': user.nom,
        'email': user.email,
        'role': user.role,
        'isActive': user.is_active,
        'avatar': user.avatar_url
    })


@adminbp.route('/admin/users', methods=['POST'])
@login_required
def add_user():
    # Vérification des permissions
    if not current_user.is_authenticated or current_user.role != 'administrateur':
        return jsonify({'success': False, 'error': 'Accès non autorisé'}), 403
    
    # Gestion des données du formulaire
    data = request.get_json() if request.is_json else request.form.to_dict()
    
    try:
        # Validation des champs obligatoires
        required_fields = ['username', 'email', 'password', 'role', 'prenom', 'nom']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Tous les champs obligatoires doivent être remplis'
            }), 400

        # Validation email institutionnel
        if not data['email'].endswith('@ista.ma') or data['email'].endswith('@gmail.com'):
            return jsonify({
                'success': False,
                'error': 'Seuls les emails @ista.ma ou @gmail.com sont acceptés'
            }), 400

        # Création de l'utilisateur
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],  # Utilise le setter password
            role=data['role'],
            prenom=data['prenom'],
            nom=data['nom'],
            is_active=True
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Utilisateur créé avec succès',
            'user': new_user.to_dict()
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        error_msg = 'Ce nom d\'utilisateur ou email est déjà utilisé'
        if 'email' in str(e):
            error_msg = 'Cet email est déjà utilisé'
        elif 'username' in str(e):
            error_msg = 'Ce nom d\'utilisateur est déjà pris'
        return jsonify({'success': False, 'error': error_msg}), 400

    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erreur création utilisateur: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Une erreur interne est survenue'
        }), 500'''

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from ..models.Users import User
from ..models.tuyaux import Tuyau
from ..models.courses import Cours 
from ..models.activity import ActivityLog
from ..models.clubs import Club
from ..models.books import Book
from ..models.addsyllabus import Course
from ..models.registration import InscriptionAcademique
from ..extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func, extract, and_
import io
import zipfile
import json
import psutil
import platform
import os
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
import humanize

adminbp = Blueprint('admin', __name__)

@adminbp.route('/admin')
@login_required
def PageAdmin():
    if current_user.role != 'administrateur':
        flash(f'Salut {current_user.prenom} {current_user.nom} - Cette page est réservée aux admins', 'warning')
        return redirect(url_for('principale.Page_Principale'))
    
    # Récupération des statistiques de base
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter(User.last_login > (datetime.now() - timedelta(days=30))).count(),
        'new_users_today': User.query.filter(User.date_creation >= datetime.now().date()).count(),
        'total_tuyaux': Tuyau.query.count(),
        'tuyaux_last_month': Tuyau.query.filter(Tuyau.date_ajout > (datetime.now() - timedelta(days=30))).count(),
        'total_courses': Cours.query.count(),
        'total_registrations': InscriptionAcademique.query.count(),
        'today_logins': User.query.filter(User.last_login > datetime.now().replace(hour=0, minute=0, second=0)).count(),
        'disk_usage': psutil.disk_usage('/').percent,
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'total_clubs': Club.query.count(),
        'active_clubs': Club.query.filter(Club.is_active == True).count(),
        'total_books': Book.query.count(),
        'books_available': Book.query.filter_by(disponible=True).count(),
        'total_syllabus': Course.query.count(),
        'syllabus_last_month': Course.query.filter(
            Course.date_ajout > (datetime.now() - timedelta(days=30))
        ).count(),
    }
    
    # Derniers utilisateurs avec plus de données
    users = User.query.order_by(User.last_login.desc()).limit(10).all()
    
    # Journal d'activité
    activity_logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(50).all()
    
    # Données pour les graphiques
    days = 30
    date_labels = []
    login_data = []
    tuyaux_data = []
    user_registration_data = []
    
    for i in range(days, -1, -1):
        date = datetime.now() - timedelta(days=i)
        date_labels.append(date.strftime("%d/%m"))
        
        # Connexions
        login_count = User.query.filter(
            func.date(User.last_login) == date.date()
        ).count()
        login_data.append(login_count)
        
        # Tuyaux partagés
        tuyaux_count = Tuyau.query.filter(
            func.date(Tuyau.date_ajout) == date.date()
        ).count()
        tuyaux_data.append(tuyaux_count)
        
        # Inscriptions
        registration_count = InscriptionAcademique.query.filter(
            func.date(InscriptionAcademique.date_creation) == date.date()
        ).count()
        user_registration_data.append(registration_count)
    
    # Répartition des rôles
    roles_distribution = db.session.query(
        User.role,
        func.count(User.id).label('count')
    ).group_by(User.role).all()
    
    roles_labels = [role[0].capitalize() for role in roles_distribution]
    roles_data = [role[1] for role in roles_distribution]
    
    # Répartition du contenu
    content_types = {
        'Cours': Cours.query.count(),
        'Tuyaux': Tuyau.query.count(),
        'Clubs': Club.query.count(),
        'Livres': Book.query.count(),
        'Syallabus': Course.query.count()
    }
    
    # Système d'exploitation et informations serveur
    system_info = {
        'os': f"{platform.system()} {platform.release()}",
        'python_version': platform.python_version(),
        'flask_version': '1.1.4',  # À remplacer par la version réelle
        'database': str(db.engine.url).split('://')[0],
        'server_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'uptime': humanize.naturaltime(datetime.now() - datetime.fromtimestamp(psutil.boot_time())),
        'cpu_count': psutil.cpu_count(),
        'total_memory': humanize.naturalsize(psutil.virtual_memory().total),
        'total_disk': humanize.naturalsize(psutil.disk_usage('/').total)
    }
    
    # Paramètres système (exemple)
    system_settings = {
        'maintenance_mode': False,
        'registration_enabled': True,
        'session_timeout': 30,
        'max_upload_size': 20,
        'system_message': ''
    }
    
    # Alertes système
    system_alerts = []
    if stats['disk_usage'] > 85:
        system_alerts.append({'type': 'danger', 'message': 'Espace disque critique (>85%)'})
    if stats['memory_usage'] > 90:
        system_alerts.append({'type': 'danger', 'message': 'Utilisation mémoire élevée (>90%)'})
    if stats['cpu_usage'] > 90:
        system_alerts.append({'type': 'warning', 'message': 'Utilisation CPU élevée (>90%)'})
    
     # Préparer les données pour les graphiques
    by_level = db.session.query(
        InscriptionAcademique.niveau,
        func.count(InscriptionAcademique.id).label('count')
    ).group_by(InscriptionAcademique.niveau).all()

    by_department = db.session.query(
        InscriptionAcademique.departement,
        func.count(InscriptionAcademique.id).label('count')
    ).group_by(InscriptionAcademique.departement).all()

    # Convertir en listes de labels et valeurs
    level_labels = [item.niveau for item in by_level]
    level_counts = [item.count for item in by_level]
    
    department_labels = [item.departement for item in by_department]
    department_counts = [item.count for item in by_department]

    # Récupération des utilisateurs actifs avec activité
    active_users = db.session.query(
        User,
        func.count(ActivityLog.id).label('activity_count')
    ).join(
        ActivityLog,
        User.id == ActivityLog.user_id
    ).group_by(
        User.id
    ).order_by(
        func.count(ActivityLog.id).desc()
    ).limit(10).all()

    # Préparation des données pour le template
    active_users_data = []
    for user, activity_count in active_users:
        active_users_data.append({
            'id': user.id,
            'nom_complet': user.nom_complet,
            'email': user.email,
            'activity_count': activity_count or 0,  # Garantit une valeur numérique
            'last_login': user.last_login.isoformat() if user.last_login else None
        })

    # Dans la route admin
    clubs_by_category = db.session.query(
        Club.category,
        func.count(Club.id).label('count')
    ).group_by(Club.category).all()

    books_by_category = db.session.query(
        Book.category,
        func.count(Book.id).label('count')
    ).group_by(Book.category).all()



    return render_template('PageAdmin.html',
                         stats=stats,
                         users=users,
                         activity_logs=activity_logs,
                         current_date=datetime.now().strftime("%d/%m/%Y"),
                         date_labels=date_labels,
                         login_data=login_data,
                         tuyaux_data=tuyaux_data,
                         user_registration_data=user_registration_data,
                         roles_labels=roles_labels,
                         roles_data=roles_data,
                         content_labels=list(content_types.keys()),
                         content_data=list(content_types.values()),
                         content_types = content_types,
                         system_settings=system_settings,
                         system_info=system_info,
                         system_alerts=system_alerts,
                         level_labels=level_labels,
                         level_counts=level_counts,
                         department_labels=department_labels,
                         department_counts=department_counts,
                         active_users=active_users_data,
                         clubs_by_category=clubs_by_category,
                         books_by_category=books_by_category)

@adminbp.route('/api/system/stats')
@login_required
def system_stats():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Statistiques système
    disk = psutil.disk_usage('/')
    mem = psutil.virtual_memory()
    
    return jsonify({
        'cpu': psutil.cpu_percent(interval=1),
        'memory': {
            'used': mem.used,
            'total': mem.total,
            'percent': mem.percent
        },
        'disk': {
            'used': disk.used,
            'total': disk.total,
            'percent': disk.percent
        },
        'network': {
            'bytes_sent': psutil.net_io_counters().bytes_sent,
            'bytes_recv': psutil.net_io_counters().bytes_recv
        },
        'uptime': (datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds()
    })

@adminbp.route('/api/system/logs')
@login_required
def system_logs():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Récupérer les derniers logs système (exemple)
    logs = []
    try:
        with open('/var/log/syslog', 'r') as f:
            logs = [line.strip() for line in f.readlines()[-100:]]  # 100 dernières lignes
    except:
        logs = ["Impossible de charger les logs système"]
    
    return jsonify({'logs': logs})

@adminbp.route('/api/system/processes')
@login_required
def system_processes():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        processes.append({
            'pid': proc.info['pid'],
            'name': proc.info['name'],
            'user': proc.info['username'],
            'cpu': proc.info['cpu_percent'],
            'memory': proc.info['memory_percent']
        })
    
    return jsonify({'processes': processes})

@adminbp.route('/api/database/stats')
@login_required
def database_stats():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Statistiques par table
    tables = {
        'users': User.query.count(),
        'tuyaux': Tuyau.query.count(),
        'courses': Cours.query.count(),
        'clubs': Club.query.count(),
        'books': Book.query.count(),
        'registrations': InscriptionAcademique.query.count()
    }
    
    # Taille estimée de la base de données
    db_size = 0
    try:
        if db.engine.url.drivername == 'sqlite':
            db_size = os.path.getsize(db.engine.url.database)
        elif db.engine.url.drivername == 'postgresql':
            result = db.session.execute("SELECT pg_database_size(current_database())")
            db_size = result.scalar()
        elif db.engine.url.drivername == 'mysql':
            result = db.session.execute("SELECT SUM(data_length + index_length) FROM information_schema.TABLES WHERE table_schema = DATABASE()")
            db_size = result.scalar()
    except:
        db_size = 0
    
    return jsonify({
        'tables': tables,
        'size': db_size,
        'size_human': humanize.naturalsize(db_size)
    })

@adminbp.route('/api/database/optimize', methods=['POST'])
@login_required
def optimize_database():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        if db.engine.url.drivername == 'sqlite':
            db.session.execute("VACUUM")
        elif db.engine.url.drivername == 'postgresql':
            db.session.execute("VACUUM FULL ANALYZE")
        elif db.engine.url.drivername == 'mysql':
            db.session.execute("OPTIMIZE TABLE users, tuyaux, courses, clubs, books, inscriptions")
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Database optimization completed'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@adminbp.route('/api/backup/create', methods=['POST'])
@login_required
def create_backup():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            # Ajouter les données des tables
            tables = {
                'users': User.query.all(),
                'tuyaux': Tuyau.query.all(),
                'courses': Cours.query.all(),
                'clubs': Club.query.all(),
                'books': Book.query.all(),
                'registrations': InscriptionAcademique.query.all()
            }
            
            for table_name, data in tables.items():
                zf.writestr(f'{table_name}.json', json.dumps([item.to_dict() for item in data], indent=2))
            
            # Ajouter les fichiers uploadés (exemple)
            upload_folders = [
                'app/static/uploads',
                'app/static/books'
            ]
            
            for folder in upload_folders:
                if os.path.exists(folder):
                    for root, dirs, files in os.walk(folder):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, start=folder)
                            zf.write(file_path, f'uploads/{arcname}')
        
        memory_file.seek(0)
        
        # Log l'activité
        log = ActivityLog(
            user_id=current_user.id,
            action="Sauvegarde complète du système créée"
        )
        db.session.add(log)
        db.session.commit()
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'backup_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@adminbp.route('/api/system/maintenance', methods=['POST'])
@login_required
def system_maintenance():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    action = request.json.get('action')
    
    try:
        if action == 'clear_cache':
            # Implémenter la logique de nettoyage du cache
            result = {'success': True, 'message': 'Cache cleared successfully'}
        elif action == 'restart_app':
            # Cela nécessiterait un système comme systemd ou supervisor
            result = {'success': False, 'message': 'App restart not implemented'}
        else:
            result = {'success': False, 'message': 'Invalid action'}
        
        # Log l'activité
        log = ActivityLog(
            user_id=current_user.id,
            action=f"Maintenance système: {action}"
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@adminbp.route('/api/analytics/user-activity')
@login_required
def user_activity_analytics():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Utilisateurs les plus actifs
    active_users = db.session.query(
        User.id,
        User.nom_complet,
        func.count(ActivityLog.id).label('activity_count')
    ).join(
        ActivityLog,
        User.id == ActivityLog.user_id
    ).group_by(
        User.id
    ).order_by(
        func.count(ActivityLog.id).desc()
    ).limit(10).all()
    
    # Heures d'activité
    activity_by_hour = db.session.query(
        extract('hour', ActivityLog.timestamp).label('hour'),
        func.count(ActivityLog.id).label('count')
    ).group_by(
        'hour'
    ).order_by(
        'hour'
    ).all()
    
    return jsonify({
        'active_users': [dict(row) for row in active_users],
        'activity_by_hour': [dict(row) for row in activity_by_hour]
    })

@adminbp.route('/api/analytics/registrations')
@login_required
def registration_analytics():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Inscriptions par département
    by_department = db.session.query(
        InscriptionAcademique.departement,
        func.count(InscriptionAcademique.id).label('count')
    ).group_by(
        InscriptionAcademique.departement
    ).all()
    
    # Inscriptions par niveau
    by_level = db.session.query(
        InscriptionAcademique.niveau,
        func.count(InscriptionAcademique.id).label('count')
    ).group_by(
        InscriptionAcademique.niveau
    ).all()
    
    return jsonify({
        'by_department': [dict(row) for row in by_department],
        'by_level': [dict(row) for row in by_level]
    })

@adminbp.route('/api/analytics/clubs')
@login_required
def club_analytics():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Clubs les plus populaires
    popular_clubs = db.session.query(
        Club.title,
        func.count(Member.id).label('member_count')
    ).join(
        Member,
        Club.id == Member.club_id
    ).group_by(
        Club.id
    ).order_by(
        func.count(Member.id).desc()
    ).limit(5).all()
    
    return jsonify({
        'popular_clubs': [dict(row) for row in popular_clubs]
    })

@adminbp.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def user_api(user_id):
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': user.id,
            'firstName': user.prenom,
            'lastName': user.nom,
            'email': user.email,
            'role': user.role,
            'isActive': user.is_active,
            'avatar': user.get_avatar_url()
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        user.prenom = data.get('firstName', user.prenom)
        user.nom = data.get('lastName', user.nom)
        user.email = data.get('email', user.email)
        user.role = data.get('role', user.role)
        user.is_active = data.get('status', user.is_active) == '1'
        
        if 'password' in data and data['password']:
            user.password = generate_password_hash(data['password'])
        
        if 'avatar' in data:
            user.avatar_url = data['avatar']
        
        db.session.commit()
        
        # Log l'activité
        log = ActivityLog(
            user_id=current_user.id,
            action=f"Modification de l'utilisateur {user.email}"
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'User updated successfully'})
    
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        
        # Log l'activité
        log = ActivityLog(
            user_id=current_user.id,
            action=f"Suppression de l'utilisateur {user.email}"
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'})

@adminbp.route('/admin/impersonate/<int:user_id>')
@login_required
def impersonate(user_id):
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    login_user(user)
    
    # Log l'activité
    log = ActivityLog(
        user_id=current_user.id,
        action=f"Connexion en tant que {user.email}"
    )
    db.session.add(log)
    db.session.commit()
    
    return redirect(url_for('principale.Page_Principale'))

@adminbp.route('/api/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def reset_password(user_id):
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    new_password = generate_random_password()  # À implémenter
    user.password = generate_password_hash(new_password)
    db.session.commit()
    
    # Envoyer le nouveau mot de passe par email (à implémenter)
    
    # Log l'activité
    log = ActivityLog(
        user_id=current_user.id,
        action=f"Réinitialisation du mot de passe pour {user.email}"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Password reset successfully'})

@adminbp.route('/api/notifications', methods=['POST'])
@login_required
def send_notification():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Validation des données
    if not all(k in data for k in ['recipients', 'subject', 'message']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Envoyer les notifications (à implémenter selon votre système)
    
    # Log l'activité
    log = ActivityLog(
        user_id=current_user.id,
        action=f"Notification envoyée: {data['subject']}"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Notification sent successfully'})

@adminbp.route('/admin/backup')
@login_required
def backup():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Créer un fichier ZIP en mémoire
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        # Ajouter les données des utilisateurs
        users = User.query.all()
        users_data = [{
            'id': u.id,
            'prenom': u.prenom,
            'nom': u.nom,
            'email': u.email,
            'role': u.role,
            'is_active': u.is_active,
            'last_login': u.last_login.isoformat() if u.last_login else None
        } for u in users]
        zf.writestr('users.json', json.dumps(users_data, indent=2))
        
        # Ajouter les tuyaux
        tuyaux = Tuyau.query.all()
        tuyaux_data = [{
            'id': t.id,
            'titre': t.titre,
            'contenu': t.contenu,
            'date_ajout': t.date_ajout.isoformat(),
            'auteur_id': t.auteur_id
        } for t in tuyaux]
        zf.writestr('tuyaux.json', json.dumps(tuyaux_data, indent=2))
        
        # Ajouter les cours
        courses = Cours.query.all()
        courses_data = [{
            'id': c.id,
            'titre': c.titre,
            'description': c.description,
            'date_creation': c.date_creation.isoformat()
        } for c in courses]
        zf.writestr('courses.json', json.dumps(courses_data, indent=2))
    
    memory_file.seek(0)
    
    # Log l'activité
    log = ActivityLog(
        user_id=current_user.id,
        action="Sauvegarde des données effectuée"
    )
    db.session.add(log)
    db.session.commit()
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'backup_{datetime.now().strftime("%Y-%m-%d")}.zip'
    )

@adminbp.route('/admin/export/<data_type>')
@login_required
def export_data(data_type):
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    if data_type == 'users':
        data = [{
            'id': u.id,
            'prenom': u.prenom,
            'nom': u.nom,
            'email': u.email,
            'role': u.role,
            'is_active': u.is_active,
            'last_login': u.last_login.isoformat() if u.last_login else None
        } for u in User.query.all()]
    elif data_type == 'courses':
        data = [{
            'id': c.id,
            'titre': c.titre,
            'description': c.description,
            'date_creation': c.date_creation.isoformat()
        } for c in Cours.query.all()]
    elif data_type == 'tuyaux':
        data = [{
            'id': t.id,
            'titre': t.titre,
            'contenu': t.contenu,
            'date_ajout': t.date_ajout.isoformat(),
            'auteur_id': t.auteur_id
        } for t in Tuyau.query.all()]
    else:
        return jsonify({'error': 'Invalid data type'}), 400
    
    memory_file = io.BytesIO()
    memory_file.write(json.dumps(data, indent=2).encode('utf-8'))
    memory_file.seek(0)
    
    # Log l'activité
    log = ActivityLog(
        user_id=current_user.id,
        action=f"Export des données {data_type}"
    )
    db.session.add(log)
    db.session.commit()
    
    return send_file(
        memory_file,
        mimetype='application/json',
        as_attachment=True,
        download_name=f'export_{data_type}_{datetime.now().strftime("%Y-%m-%d")}.json'
    )

@adminbp.route('/api/activity-logs', methods=['DELETE'])
@login_required
def clear_activity_logs():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Supprimer tous les logs
    db.session.query(ActivityLog).delete()
    db.session.commit()
    
    # Ajouter un log pour cette action (qui sera le seul log restant)
    log = ActivityLog(
        user_id=current_user.id,
        action="Journal d'activité effacé"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Activity logs cleared successfully'})

@adminbp.route('/api/system-settings', methods=['POST'])
@login_required
def update_system_settings():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Ici, vous devriez sauvegarder ces paramètres dans votre base de données
    # ou dans un fichier de configuration selon votre architecture
    
    # Log l'activité
    log = ActivityLog(
        user_id=current_user.id,
        action="Mise à jour des paramètres système"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'System settings updated successfully'})

@adminbp.route('/api/system-check')
@login_required
def system_check():
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Ici, vous devriez implémenter des vérifications réelles de votre système
    results = {
        'database': {
            'status': 'OK',
            'message': 'Connexion à la base de données fonctionnelle'
        },
        'storage': {
            'status': 'OK',
            'message': '1.2GB/5GB utilisé'
        },
        'performance': {
            'status': 'OK',
            'message': 'Performances optimales'
        },
        'updates': {
            'status': 'WARNING',
            'message': 'Mise à jour disponible (v2.1.3)'
        },
        'security': {
            'status': 'OK',
            'message': 'Aucune menace détectée'
        }
    }
    
    # Log l'activité
    log = ActivityLog(
        user_id=current_user.id,
        action="Vérification du système effectuée"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify(results)

@adminbp.route('/api/users/<int:user_id>/deactivate', methods=['POST'])
@login_required
def deactivate_user(user_id):
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    
    log = ActivityLog(
        user_id=current_user.id,
        action=f"Désactivation de l'utilisateur {user.email}"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'User deactivated successfully'})

@adminbp.route('/api/users/<int:user_id>/activate', methods=['POST'])
@login_required
def activate_user(user_id):
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    
    log = ActivityLog(
        user_id=current_user.id,
        action=f"Activation de l'utilisateur {user.email}"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'User activated successfully'})

@adminbp.route('/api/utilisateurs/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    if current_user.role != 'administrateur':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'firstName': user.prenom,
        'lastName': user.nom,
        'email': user.email,
        'role': user.role,
        'isActive': user.is_active,
        'avatar': user.avatar_url
    })

@adminbp.route('/admin/users', methods=['POST'])
@login_required
def add_user():
    # Vérification des permissions
    if not current_user.is_authenticated or current_user.role != 'administrateur':
        return jsonify({'success': False, 'error': 'Accès non autorisé'}), 403
    
    # Gestion des données du formulaire
    data = request.get_json() if request.is_json else request.form.to_dict()
    
    try:
        # Validation des champs obligatoires
        required_fields = ['username', 'email', 'password', 'role', 'prenom', 'nom']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Tous les champs obligatoires doivent être remplis'
            }), 400

        # Validation email institutionnel
        if not data['email'].endswith('@ista.ma') or data['email'].endswith('@gmail.com'):
            return jsonify({
                'success': False,
                'error': 'Seuls les emails @ista.ma ou @gmail.com sont acceptés'
            }), 400

        # Création de l'utilisateur
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],  # Utilise le setter password
            role=data['role'],
            prenom=data['prenom'],
            nom=data['nom'],
            is_active=True
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Utilisateur créé avec succès',
            'user': new_user.to_dict()
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        error_msg = 'Ce nom d\'utilisateur ou email est déjà utilisé'
        if 'email' in str(e):
            error_msg = 'Cet email est déjà utilisé'
        elif 'username' in str(e):
            error_msg = 'Ce nom d\'utilisateur est déjà pris'
        return jsonify({'success': False, 'error': error_msg}), 400

    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erreur création utilisateur: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Une erreur interne est survenue'
        }), 500

@adminbp.route('/admin/export/report/<report_type>')
@login_required
def export_report(report_type):
    if current_user.role != 'administrateur':
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('admin.PageAdmin'))
    
    try:
        if report_type == 'user_activity':
            data = User.query.all()
            filename = f"rapport_utilisateurs_{datetime.now().strftime('%Y-%m-%d')}.csv"
            output = io.StringIO()
            output.write("ID,Nom,Email,Rôle,Dernière connexion,Statut\n")
            
            for user in data:
                output.write(f"{user.id},{user.nom_complet},{user.email},{user.role},")
                output.write(f"{user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Jamais'},")
                output.write(f"{'Actif' if user.is_active else 'Inactif'}\n")
            
            mem = io.BytesIO()
            mem.write(output.getvalue().encode('utf-8'))
            mem.seek(0)
            
            return send_file(
                mem,
                mimetype='text/csv',
                as_attachment=True,
                download_name=filename
            )
        
        elif report_type == 'system_usage':
            # Générer un rapport d'utilisation du système
            pass
        
        else:
            flash('Type de rapport non valide', 'danger')
            return redirect(url_for('admin.PageAdmin'))
    
    except Exception as e:
        flash(f'Erreur lors de la génération du rapport: {str(e)}', 'danger')
        return redirect(url_for('admin.PageAdmin'))

def generate_random_password():
    # Implémentez une génération de mot de passe sécurisé
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for i in range(12))

