"""
Système de permissions et contrôle d'accès
"""
from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user


class Permission:
    """Définition des permissions"""
    # Permissions de base
    VIEW_PUBLIC = 0x01
    VIEW_COURSES = 0x02
    VIEW_GRADES = 0x04
    
    # Gestion académique
    MANAGE_COURSES = 0x08
    MANAGE_EVALUATIONS = 0x10
    MANAGE_GRADES = 0x20
    MANAGE_SCHEDULES = 0x40
    
    # Gestion des enseignants
    VIEW_TEACHERS = 0x80
    MANAGE_TEACHERS = 0x100
    ASSIGN_TEACHERS = 0x200
    
    # Administration
    MANAGE_USERS = 0x400
    MANAGE_SETTINGS = 0x800
    VIEW_STATS = 0x1000
    GENERATE_REPORTS = 0x2000
    
    # Super admin
    ADMIN = 0xFFFF


class Role:
    """Rôles prédéfinis avec leurs permissions"""
    ROLES = {
        'etudiant': {
            'name': 'Étudiant',
            'permissions': (
                Permission.VIEW_PUBLIC |
                Permission.VIEW_COURSES |
                Permission.VIEW_GRADES
            ),
            'description': 'Accès consultation des cours et résultats'
        },
        'enseignant': {
            'name': 'Enseignant',
            'permissions': (
                Permission.VIEW_PUBLIC |
                Permission.VIEW_COURSES |
                Permission.MANAGE_EVALUATIONS |
                Permission.MANAGE_GRADES |
                Permission.VIEW_TEACHERS
            ),
            'description': 'Gestion des évaluations et notes de ses cours'
        },
        'coordinateur': {
            'name': 'Coordinateur pédagogique',
            'permissions': (
                Permission.VIEW_PUBLIC |
                Permission.VIEW_COURSES |
                Permission.MANAGE_COURSES |
                Permission.MANAGE_EVALUATIONS |
                Permission.MANAGE_SCHEDULES |
                Permission.VIEW_TEACHERS |
                Permission.ASSIGN_TEACHERS |
                Permission.VIEW_STATS
            ),
            'description': 'Gestion pédagogique d\'une filière ou département'
        },
        'administrateur': {
            'name': 'Administrateur',
            'permissions': Permission.ADMIN,
            'description': 'Accès complet à toutes les fonctionnalités'
        }
    }
    
    @staticmethod
    def get_permissions(role_name):
        """Récupère les permissions d'un rôle"""
        return Role.ROLES.get(role_name, {}).get('permissions', 0)
    
    @staticmethod
    def has_permission(role_name, permission):
        """Vérifie si un rôle a une permission"""
        role_perms = Role.get_permissions(role_name)
        return (role_perms & permission) == permission


def permission_required(permission):
    """Décorateur pour vérifier les permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Vous devez être connecté pour accéder à cette page', 'warning')
                return redirect(url_for('auth.login'))
            
            if not Role.has_permission(current_user.role, permission):
                flash('Vous n\'avez pas les permissions nécessaires', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Décorateur pour accès administrateur uniquement"""
    return permission_required(Permission.ADMIN)(f)


def enseignant_or_admin_required(f):
    """Décorateur pour enseignants et administrateurs"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vous devez être connecté', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role not in ['enseignant', 'coordinateur', 'administrateur']:
            flash('Accès réservé aux enseignants et administrateurs', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def own_resource_or_admin(resource_owner_id):
    """Vérifie si l'utilisateur est propriétaire de la ressource ou admin"""
    if current_user.role == 'administrateur':
        return True
    return current_user.id == resource_owner_id


def can_manage_evaluation(evaluation):
    """Vérifie si l'utilisateur peut gérer une évaluation"""
    if current_user.role == 'administrateur':
        return True
    
    if current_user.role == 'enseignant':
        # Vérifier si l'enseignant enseigne cette UE
        from app.models.enseignants import AffectationCours
        affectation = AffectationCours.query.filter_by(
            enseignant_id=current_user.enseignant.id,
            unite_enseignement_id=evaluation.ue_id,
            est_active=True
        ).first()
        return affectation is not None
    
    return False


def can_view_student_grades(etudiant_id):
    """Vérifie si l'utilisateur peut voir les notes d'un étudiant"""
    if current_user.role == 'administrateur':
        return True
    
    if current_user.role == 'etudiant':
        return current_user.id == etudiant_id
    
    if current_user.role == 'enseignant':
        # Un enseignant peut voir les notes de ses étudiants
        from app.models.academique import Note, Evaluation, InscriptionClasse
        from app.models.enseignants import AffectationCours
        
        # Récupérer les classes de l'enseignant
        affectations = AffectationCours.query.filter_by(
            enseignant_id=current_user.enseignant.id,
            est_active=True
        ).all()
        
        classes_ids = [aff.classe_id for aff in affectations]
        
        # Vérifier si l'étudiant est dans une de ces classes
        inscription = InscriptionClasse.query.filter_by(
            etudiant_id=etudiant_id,
            est_active=True
        ).filter(InscriptionClasse.classe_id.in_(classes_ids)).first()
        
        return inscription is not None
    
    return False


class PermissionChecker:
    """Classe utilitaire pour vérifications de permissions complexes"""
    
    @staticmethod
    def can_modify_enseignant(enseignant_id):
        """Peut modifier un enseignant"""
        if current_user.role == 'administrateur':
            return True
        
        if current_user.role == 'enseignant':
            # Un enseignant ne peut modifier que son propre profil
            return current_user.enseignant and current_user.enseignant.id == enseignant_id
        
        return False
    
    @staticmethod
    def can_assign_course():
        """Peut affecter un cours"""
        return Role.has_permission(current_user.role, Permission.ASSIGN_TEACHERS)
    
    @staticmethod
    def can_create_evaluation():
        """Peut créer une évaluation"""
        return Role.has_permission(current_user.role, Permission.MANAGE_EVALUATIONS)
    
    @staticmethod
    def can_publish_grades():
        """Peut publier des notes"""
        return current_user.role in ['enseignant', 'coordinateur', 'administrateur']
    
    @staticmethod
    def can_view_statistics():
        """Peut voir les statistiques"""
        return Role.has_permission(current_user.role, Permission.VIEW_STATS)
    
    @staticmethod
    def can_generate_reports():
        """Peut générer des rapports"""
        return Role.has_permission(current_user.role, Permission.GENERATE_REPORTS)
    
    @staticmethod
    def can_manage_schedule():
        """Peut gérer les emplois du temps"""
        return Role.has_permission(current_user.role, Permission.MANAGE_SCHEDULES)
    
    @staticmethod
    def can_send_notifications():
        """Peut envoyer des notifications"""
        return current_user.role in ['coordinateur', 'administrateur']


def register_permission_context_processor(app):
    """Enregistre les permissions dans le contexte des templates"""
    @app.context_processor
    def inject_permissions():
        return {
            'Permission': Permission,
            'Role': Role,
            'PermissionChecker': PermissionChecker,
            'has_permission': lambda perm: Role.has_permission(current_user.role, perm) if current_user.is_authenticated else False
        }
