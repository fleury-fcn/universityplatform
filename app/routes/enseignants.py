"""
Routes pour la gestion des enseignants
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from app.extensions import db
from app.models.enseignants import (
    Enseignant, DocumentEnseignant, AffectationCours, 
    PresenceEnseignant, DisponibiliteEnseignant, DepartementAcademique
)
from app.models.academique import UniteEnseignement, Classe, SeanceCours
from app.permissions import admin_required, PermissionChecker
from werkzeug.utils import secure_filename
import os
from sqlalchemy import or_

enseignants_bp = Blueprint('enseignants', __name__, url_prefix='/enseignants')


@enseignants_bp.route('/')
@login_required
@admin_required
def liste_enseignants():
    """Liste tous les enseignants"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filtres
    statut = request.args.get('statut', '')
    departement_id = request.args.get('departement', type=int)
    search = request.args.get('search', '')
    
    query = Enseignant.query
    
    if statut:
        query = query.filter_by(statut=statut)
    if departement_id:
        query = query.filter_by(departement_id=departement_id)
    if search:
        query = query.filter(
            or_(
                Enseignant.nom.ilike(f'%{search}%'),
                Enseignant.prenom.ilike(f'%{search}%'),
                Enseignant.matricule.ilike(f'%{search}%'),
                Enseignant.email_professionnel.ilike(f'%{search}%')
            )
        )
    
    enseignants = query.order_by(Enseignant.nom).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    departements = DepartementAcademique.query.filter_by(est_actif=True).all()
    
    # Statistiques
    stats = {
        'total': Enseignant.query.count(),
        'actifs': Enseignant.query.filter_by(statut='actif').count(),
        'temps_plein': Enseignant.query.filter_by(type_emploi='temps_plein').count(),
        'surcharges': Enseignant.query.filter(
            Enseignant.charge_horaire_totale > Enseignant.volume_horaire_annuel
        ).count()
    }
    
    return render_template('enseignants/liste.html',
                         enseignants=enseignants,
                         departements=departements,
                         stats=stats)


@enseignants_bp.route('/nouveau', methods=['GET', 'POST'])
@login_required
@admin_required
def nouveau_enseignant():
    """Créer un nouveau dossier enseignant"""
    if request.method == 'POST':
        try:
            # Génération automatique du matricule
            dernier = Enseignant.query.order_by(Enseignant.id.desc()).first()
            numero = (dernier.id + 1) if dernier else 1
            matricule = f"ENS{date.today().year}{numero:04d}"
            
            enseignant = Enseignant(
                matricule=matricule,
                nom=request.form.get('nom'),
                prenom=request.form.get('prenom'),
                genre=request.form.get('genre'),
                date_naissance=datetime.strptime(request.form.get('date_naissance'), '%Y-%m-%d').date() if request.form.get('date_naissance') else None,
                email_professionnel=request.form.get('email_professionnel'),
                email_personnel=request.form.get('email_personnel'),
                telephone_mobile=request.form.get('telephone_mobile'),
                grade=request.form.get('grade'),
                specialite=request.form.get('specialite'),
                departement_id=request.form.get('departement_id', type=int),
                type_emploi=request.form.get('type_emploi'),
                heures_disponibles=request.form.get('heures_disponibles', type=int),
                volume_horaire_annuel=request.form.get('volume_horaire_annuel', type=int),
                date_recrutement=datetime.strptime(request.form.get('date_recrutement'), '%Y-%m-%d').date() if request.form.get('date_recrutement') else None,
                statut='actif'
            )
            
            db.session.add(enseignant)
            db.session.commit()
            
            flash(f'Enseignant {enseignant.nom_complet} créé avec succès! Matricule: {matricule}', 'success')
            return redirect(url_for('enseignants.fiche_enseignant', id=enseignant.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création: {str(e)}', 'danger')
    
    departements = DepartementAcademique.query.filter_by(est_actif=True).all()
    return render_template('enseignants/formulaire.html', 
                         departements=departements,
                         action='Créer',
                         enseignant=None)


@enseignants_bp.route('/<int:id>')
@login_required
def fiche_enseignant(id):
    """Fiche détaillée d'un enseignant"""
    enseignant = Enseignant.query.get_or_404(id)
    
    if not PermissionChecker.can_modify_enseignant(id):
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('main.Page_Accueil'))
    
    # Charger les affectations actives
    affectations = enseignant.affectations.filter_by(est_active=True).all()
    
    # Documents
    documents = enseignant.documents.order_by(DocumentEnseignant.date_ajout.desc()).limit(10).all()
    
    # Statistiques de présence
    total_seances = PresenceEnseignant.query.filter_by(enseignant_id=id).count()
    absences = PresenceEnseignant.query.filter_by(enseignant_id=id, statut='absent').count()
    taux_presence = round((total_seances - absences) / total_seances * 100, 1) if total_seances > 0 else 100
    
    return render_template('enseignants/fiche.html',
                         enseignant=enseignant,
                         affectations=affectations,
                         documents=documents,
                         taux_presence=taux_presence)


@enseignants_bp.route('/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
@admin_required
def modifier_enseignant(id):
    """Modifier un enseignant"""
    enseignant = Enseignant.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            enseignant.nom = request.form.get('nom')
            enseignant.prenom = request.form.get('prenom')
            enseignant.genre = request.form.get('genre')
            enseignant.email_professionnel = request.form.get('email_professionnel')
            enseignant.email_personnel = request.form.get('email_personnel')
            enseignant.telephone_mobile = request.form.get('telephone_mobile')
            enseignant.grade = request.form.get('grade')
            enseignant.specialite = request.form.get('specialite')
            enseignant.departement_id = request.form.get('departement_id', type=int)
            enseignant.type_emploi = request.form.get('type_emploi')
            enseignant.heures_disponibles = request.form.get('heures_disponibles', type=int)
            enseignant.volume_horaire_annuel = request.form.get('volume_horaire_annuel', type=int)
            enseignant.statut = request.form.get('statut')
            
            if request.form.get('date_naissance'):
                enseignant.date_naissance = datetime.strptime(request.form.get('date_naissance'), '%Y-%m-%d').date()
            if request.form.get('date_recrutement'):
                enseignant.date_recrutement = datetime.strptime(request.form.get('date_recrutement'), '%Y-%m-%d').date()
            
            db.session.commit()
            flash('Enseignant modifié avec succès', 'success')
            return redirect(url_for('enseignants.fiche_enseignant', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification: {str(e)}', 'danger')
    
    departements = DepartementAcademique.query.filter_by(est_actif=True).all()
    return render_template('enseignants/formulaire.html',
                         enseignant=enseignant,
                         departements=departements,
                         action='Modifier')


@enseignants_bp.route('/<int:id>/affectations')
@login_required
@admin_required
def affectations_enseignant(id):
    """Gérer les affectations d'un enseignant"""
    enseignant = Enseignant.query.get_or_404(id)
    
    # Affectations actives
    affectations_actives = enseignant.affectations.filter_by(est_active=True).all()
    
    # Historique
    historique = enseignant.affectations.filter_by(est_active=False).order_by(
        AffectationCours.date_affectation.desc()
    ).limit(20).all()
    
    # UE disponibles
    ues_disponibles = UniteEnseignement.query.filter_by(est_active=True).all()
    classes_disponibles = Classe.query.filter_by(est_active=True).all()
    
    current_year = datetime.now().year
    return render_template('enseignants/affectations.html',
                         enseignant=enseignant,
                         affectations_actives=affectations_actives,
                         historique=historique,
                         ues_disponibles=ues_disponibles,
                         classes_disponibles=classes_disponibles,
                         current_year=f"{current_year}-{current_year+1}")


@enseignants_bp.route('/<int:id>/affecter', methods=['POST'])
@login_required
@admin_required
def affecter_cours(id):
    """Affecter un enseignant à un cours"""
    enseignant = Enseignant.query.get_or_404(id)
    
    try:
        affectation = AffectationCours(
            enseignant_id=id,
            unite_enseignement_id=request.form.get('ue_id', type=int),
            classe_id=request.form.get('classe_id', type=int),
            annee_academique=request.form.get('annee_academique'),
            semestre=request.form.get('semestre', type=int),
            type_intervention=request.form.get('type_intervention'),
            volume_horaire=request.form.get('volume_horaire', type=int),
            date_debut=datetime.strptime(request.form.get('date_debut'), '%Y-%m-%d').date(),
            affecte_par_id=current_user.id,
            est_active=True
        )
        
        db.session.add(affectation)
        
        # Recalculer la charge horaire
        enseignant.calculer_charge_horaire()
        
        db.session.commit()
        
        flash('Affectation créée avec succès', 'success')
        
        # Vérifier surcharge
        if enseignant.est_surcharge:
            flash(f'Attention: {enseignant.nom_complet} est en surcharge ({enseignant.charge_horaire_pourcent}%)', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de l\'affectation: {str(e)}', 'danger')
    
    return redirect(url_for('enseignants.affectations_enseignant', id=id))


@enseignants_bp.route('/affectation/<int:aff_id>/desactiver', methods=['POST'])
@login_required
@admin_required
def desactiver_affectation(aff_id):
    """Désactiver une affectation"""
    affectation = AffectationCours.query.get_or_404(aff_id)
    
    try:
        affectation.est_active = False
        affectation.date_fin = date.today()
        
        # Recalculer la charge horaire
        affectation.enseignant.calculer_charge_horaire()
        
        db.session.commit()
        flash('Affectation désactivée', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur: {str(e)}', 'danger')
    
    return redirect(url_for('enseignants.affectations_enseignant', id=affectation.enseignant_id))


@enseignants_bp.route('/<int:id>/presences')
@login_required
def presences_enseignant(id):
    """Consulter les présences d'un enseignant"""
    enseignant = Enseignant.query.get_or_404(id)
    
    if not PermissionChecker.can_modify_enseignant(id):
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('main.Page_Accueil'))
    
    page = request.args.get('page', 1, type=int)
    presences = enseignant.presences.order_by(
        PresenceEnseignant.date_seance.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    # Statistiques
    total = enseignant.presences.count()
    absences = enseignant.presences.filter_by(statut='absent').count()
    retards = enseignant.presences.filter_by(statut='retard').count()
    
    stats = {
        'total': total,
        'presences': total - absences - retards,
        'absences': absences,
        'retards': retards,
        'taux_presence': round((total - absences) / total * 100, 1) if total > 0 else 100
    }
    
    return render_template('enseignants/presences.html',
                         enseignant=enseignant,
                         presences=presences,
                         stats=stats)


@enseignants_bp.route('/<int:id>/documents')
@login_required
def documents_enseignant(id):
    """Gérer les documents d'un enseignant"""
    enseignant = Enseignant.query.get_or_404(id)
    
    if not PermissionChecker.can_modify_enseignant(id):
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('main.Page_Accueil'))
    
    documents = enseignant.documents.order_by(DocumentEnseignant.date_ajout.desc()).all()
    
    return render_template('enseignants/documents.html',
                         enseignant=enseignant,
                         documents=documents)


@enseignants_bp.route('/<int:id>/statistiques')
@login_required
@admin_required
def statistiques_enseignant(id):
    """Statistiques détaillées d'un enseignant"""
    enseignant = Enseignant.query.get_or_404(id)
    
    # Calculs statistiques
    stats = {
        'charge_horaire': {
            'totale': enseignant.charge_horaire_totale,
            'volume_annuel': enseignant.volume_horaire_annuel,
            'pourcentage': enseignant.charge_horaire_pourcent,
            'est_surcharge': enseignant.est_surcharge
        },
        'affectations': {
            'actives': enseignant.affectations.filter_by(est_active=True).count(),
            'total': enseignant.affectations.count()
        },
        'presences': {
            'total': enseignant.presences.count(),
            'absences': enseignant.presences.filter_by(statut='absent').count(),
            'retards': enseignant.presences.filter_by(statut='retard').count()
        }
    }
    
    # Répartition par type d'intervention
    repartition = db.session.query(
        AffectationCours.type_intervention,
        db.func.sum(AffectationCours.volume_horaire)
    ).filter(
        AffectationCours.enseignant_id == id,
        AffectationCours.est_active == True
    ).group_by(AffectationCours.type_intervention).all()
    
    return render_template('enseignants/statistiques.html',
                         enseignant=enseignant,
                         stats=stats,
                         repartition=repartition)


@enseignants_bp.route('/api/charge-horaire')
@login_required
@admin_required
def api_charge_horaire():
    """API pour récupérer la charge horaire de tous les enseignants"""
    enseignants = Enseignant.query.filter_by(statut='actif').all()
    
    data = []
    for ens in enseignants:
        data.append({
            'id': ens.id,
            'nom': ens.nom_complet,
            'charge': ens.charge_horaire_totale,
            'volume_annuel': ens.volume_horaire_annuel,
            'pourcentage': ens.charge_horaire_pourcent,
            'est_surcharge': ens.est_surcharge
        })
    
    return jsonify(data)
