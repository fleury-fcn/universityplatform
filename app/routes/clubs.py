from flask import Blueprint, current_app, request, jsonify, render_template, url_for
from ..extensions import db
from ..models.clubs import Club, Member
from flask_login import current_user, login_required
import logging
from functools import wraps

clubsbp = Blueprint('clubs', __name__, url_prefix='/clubs')

# Helper function to check admin permissions
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'administrateur':
            return jsonify({"success": False, "message": "Permission refusée"}), 403
        return f(*args, **kwargs)
    return decorated_function

# Route pour la page principale des clubs
@clubsbp.route('/', methods=['GET'])
@login_required
def clubs_page():
    try:
        # Charge les clubs avec leurs membres et les informations utilisateur nécessaires
        clubs = Club.query.options(
            db.joinedload(Club.members).joinedload(Member.user)
        ).filter_by(is_active=True).order_by(Club.title.asc()).all()
    
        clubs_data = []
        for club in clubs:
            current_member = next(
                (m for m in club.members if m.user_id == current_user.id), 
                None
            )
            
            is_member = current_member is not None
            is_admin = current_user.role == 'administrateur' or current_user.id == club.admin_id
            is_etudiant = current_user.role == 'etudiant'

            clubs_data.append({
                'id': club.id,
                'title': club.title,
                'description': club.description,
                'category': club.category,
                'banner_url': club.banner or url_for('static', filename='images/clubs/default-banner.jpg'),
                'logo_url': club.logo or url_for('static', filename='images/clubs/default-logo.jpg'),
                'meeting_frequency': club.meeting_frequency or "Réunion hebdomadaire",
                'member_count': len(club.members),
                'is_member': is_member,
                'is_admin': is_admin,
                'is_etudiant': is_etudiant,
                'current_user_id': current_user.id,
                'members': [{
                    'id': m.id,
                    'first_name': m.first_name,
                    'last_name': m.last_name,
                    'department': m.department,
                    'user_id': m.user_id,
                    'can_remove': is_admin or m.user_id == current_user.id
                } for m in club.members],
                'tags': club.tags.split(',') if club.tags else []
            })

        return render_template('PageClubs.html', clubs=clubs_data)
        
    except Exception as e:
        current_app.logger.error(f"Error in clubs_page: {str(e)}", exc_info=True)
        return render_template('error.html', error="Une erreur est survenue"), 500

@clubsbp.route('/<int:club_id>', methods=['GET'])
@login_required
def club_detail(club_id):
    try:
        # Chargement du club avec les membres et leurs utilisateurs associés
        club = Club.query.options(
            db.joinedload(Club.members).joinedload(Member.user)
        ).get_or_404(club_id)
        
        # Vérification des permissions
        is_admin = current_user.role == 'administrateur' or current_user.id == club.admin_id
        current_member = next(
            (m for m in club.members if m.user_id == current_user.id), 
            None
        )
        
        # Préparation des données des membres
        members_data = [{
            'id': m.id,
            'user_id': m.user_id,
            'full_name': f"{m.first_name} {m.last_name}",
            'level': m.level,
            'department': m.department,
            'joined_at': m.joined_at.strftime('%d/%m/%Y'),
            'can_remove': is_admin or (current_user.id == m.user_id),
            'is_current_user': current_user.id == m.user_id
        } for m in club.members]
        
        # Tri des membres par date d'adhésion (les plus récents en premier)
        members_data.sort(key=lambda x: x['joined_at'], reverse=True)
        
        return render_template(
            'club_detail.html',
            club={
                'id': club.id,
                'title': club.title,
                'description': club.description,
                'category': club.category,
                'banner_url': club.banner or url_for('static', filename='images/clubs/default-banner.jpg'),
                'logo_url': club.logo or url_for('static', filename='images/clubs/default-logo.jpg'),
                'meeting_frequency': club.meeting_frequency,
                'member_count': len(club.members),
                'is_member': current_member is not None,
                'is_admin': is_admin,
                'admin_id': club.admin_id,
                'created_at': club.created_at.strftime('%d %B %Y'),
                'members': members_data,
                'tags': [tag.strip() for tag in club.tags.split(',')] if club.tags else []
            },
            current_user=current_user
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in club_detail: {str(e)}", exc_info=True)
        return render_template('error.html', error="Une erreur est survenue"), 500

# Route pour rejoindre un club
@clubsbp.route('/<int:club_id>/join', methods=['POST'])
@login_required
def join_club(club_id):
    try:
        # Vérifier si le club existe et est actif
        club = Club.query.filter_by(id=club_id, is_active=True).first_or_404()
        
        # Accepte à la fois JSON et form-data
        data = request.get_json() if request.is_json else request.form

        # Validation des données
        required_fields = ['firstName', 'lastName', 'level', 'department']
        if not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "message": f"Champs manquants: {', '.join(set(required_fields) - set(data.keys()))}"
            }), 400

        # Vérification membre existant
        if Member.query.filter_by(club_id=club_id, user_id=current_user.id).first():
            return jsonify({
                "success": False,
                "message": "Vous êtes déjà membre de ce club"
            }), 400

        new_member = Member(
            first_name=data['firstName'],
            last_name=data['lastName'],
            level=data['level'],
            department=data['department'],
            academic_year=data.get('academicYear', '2023-2024'),
            club_id=club_id,
            user_id=current_user.id
        )
        
        db.session.add(new_member)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Adhésion réussie",
            "member": {
                "id": new_member.id,
                "name": f"{new_member.first_name} {new_member.last_name}"
            },
            "member_count": Member.query.filter_by(club_id=club_id).count()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur join_club: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Erreur serveur: {str(e)}"
        }), 500

# Route pour quitter un club
@clubsbp.route('/<int:club_id>/leave', methods=['POST'])
@login_required
def leave_club(club_id):
    try:
        member = Member.query.filter_by(
            club_id=club_id,
            user_id=current_user.id
        ).first_or_404()
        
        db.session.delete(member)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Vous avez quitté le club",
            "member_count": Member.query.filter_by(club_id=club_id).count()
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erreur leave_club: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur lors de la sortie"}), 500

# Route pour supprimer un membre d'un club
@clubsbp.route('/members/<int:member_id>', methods=['DELETE'])
@login_required
def remove_member(member_id):
    try:
        member = Member.query.get_or_404(member_id)
        club = Club.query.get_or_404(member.club_id)
        
        # Vérification des permissions
        if not (current_user.role == 'administrateur' or 
                current_user.id == club.admin_id or
                current_user.id == member.user_id):
            return jsonify({"success": False, "message": "Permission refusée"}), 403
        
        db.session.delete(member)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Membre supprimé",
            "member_count": Member.query.filter_by(club_id=club.id).count()
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erreur remove_member: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Erreur de suppression"}), 500

# Section Admin - Gestion des clubs
@clubsbp.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_clubs():
    if request.method == 'POST':
        try:
            # Gestion de la création d'un nouveau club
            data = request.get_json() if request.is_json else request.form
            
            new_club = Club(
                title=data.get('title'),
                description=data.get('description'),
                category=data.get('category'),
                tags=data.get('tags'),
                meeting_frequency=data.get('meeting_frequency'),
                admin_id=current_user.id,
                is_active=data.get('is_active', 'off') == 'on'
            )
            
            db.session.add(new_club)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "Club créé avec succès",
                "club_id": new_club.id
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating club: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "message": f"Erreur lors de la création: {str(e)}"
            }), 500

    # Pour GET, afficher tous les clubs avec plus de détails
    clubs = Club.query.options(
        db.joinedload(Club.members)
    ).order_by(Club.created_at.desc()).all()

    return render_template('admin_clubs.html', clubs=clubs)

# Route pour activer/désactiver un club
@clubsbp.route('/<int:club_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_club_active(club_id):
    try:
        club = Club.query.get_or_404(club_id)
        club.is_active = not club.is_active
        db.session.commit()
        
        return jsonify({
            "success": True,
            "is_active": club.is_active,
            "message": f"Club {'activé' if club.is_active else 'désactivé'} avec succès"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# Route pour supprimer un club
@clubsbp.route('/<int:club_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_club(club_id):
    try:
        club = Club.query.get_or_404(club_id)
        
        # Supprimez d'abord tous les membres pour éviter les erreurs de clé étrangère
        Member.query.filter_by(club_id=club_id).delete()
        
        db.session.delete(club)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Club supprimé avec succès",
            "deleted_id": club_id  # Renvoyez l'ID pour vérification côté client
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete club error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la suppression: {str(e)}"
        }), 500
    
# Route utilitaire pour vérifier l'appartenance à un club
@clubsbp.route('/<int:club_id>/check-member/<int:user_id>')
@login_required
def check_member(club_id, user_id):
    is_member = Member.query.filter_by(
        club_id=club_id,
        user_id=user_id
    ).first() is not None
    
    return jsonify({
        'is_member': is_member,
        'club_id': club_id,
        'user_id': user_id
    })

