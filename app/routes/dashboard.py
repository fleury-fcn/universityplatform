"""
Dashboard administratif avec statistiques et rapports
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app.extensions import db
from app.models.enseignants import Enseignant, AffectationCours, PresenceEnseignant
from app.models.academique import (
    UniteEnseignement, Classe, Evaluation, Note, ReleveNotes, SeanceCours
)
from app.models.Users import User
from app.models.actualites import Actualite
from app.models.notifications import Notification
from app.permissions import admin_required, permission_required, Permission
from sqlalchemy import func, and_, or_, extract
from collections import defaultdict

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
@admin_required
def index():
    """Dashboard principal administrateur"""
    
    # Statistiques globales
    stats = {
        'utilisateurs': {
            'total': User.query.filter_by(is_active=True).count(),
            'etudiants': User.query.filter_by(role='etudiant', is_active=True).count(),
            'enseignants': Enseignant.query.filter_by(statut='actif').count(),
            'administrateurs': User.query.filter_by(role='administrateur', is_active=True).count()
        },
        'academique': {
            'ues': UniteEnseignement.query.filter_by(est_active=True).count(),
            'classes': Classe.query.filter_by(est_active=True).count(),
            'evaluations': Evaluation.query.count(),
            'notes_saisies': Note.query.filter(Note.note.isnot(None)).count()
        },
        'enseignants': {
            'actifs': Enseignant.query.filter_by(statut='actif').count(),
            'surcharges': Enseignant.query.filter(
                Enseignant.charge_horaire_totale > Enseignant.volume_horaire_annuel
            ).count(),
            'sous_charges': Enseignant.query.filter(
                Enseignant.charge_horaire_totale < Enseignant.volume_horaire_annuel * 0.8
            ).count()
        },
        'notifications': {
            'total_aujourd_hui': Notification.query.filter(
                func.date(Notification.date_creation) == date.today()
            ).count(),
            'non_lues': Notification.query.filter_by(est_lue=False).count()
        }
    }
    
    # Activités récentes
    activites = {
        'evaluations_recentes': Evaluation.query.order_by(
            Evaluation.date_creation.desc()
        ).limit(5).all(),
        'actualites_recentes': Actualite.query.order_by(
            Actualite.date_publication.desc()
        ).limit(5).all(),
        'nouveaux_utilisateurs': User.query.order_by(
            User.created_at.desc()
        ).limit(5).all()
    }
    
    # Alertes
    alertes = []
    
    # Enseignants en surcharge
    surcharges = Enseignant.query.filter(
        Enseignant.charge_horaire_totale > Enseignant.volume_horaire_annuel,
        Enseignant.statut == 'actif'
    ).all()
    if surcharges:
        alertes.append({
            'type': 'warning',
            'titre': 'Enseignants en surcharge',
            'message': f'{len(surcharges)} enseignant(s) dépassent leur volume horaire',
            'lien': '/enseignants?surcharge=1'
        })
    
    # Évaluations sans notes
    evals_sans_notes = Evaluation.query.outerjoin(Note).filter(
        Note.id.is_(None),
        Evaluation.date_evaluation < datetime.now() - timedelta(days=7)
    ).count()
    if evals_sans_notes > 0:
        alertes.append({
            'type': 'danger',
            'titre': 'Évaluations sans notes',
            'message': f'{evals_sans_notes} évaluation(s) de plus de 7 jours sans saisie de notes',
            'lien': '/academique/evaluations'
        })
    
    # Absences enseignants non justifiées
    absences_non_justifiees = PresenceEnseignant.query.filter_by(
        statut='absent'
    ).filter(
        PresenceEnseignant.justification.is_(None),
        PresenceEnseignant.date_seance >= date.today() - timedelta(days=30)
    ).count()
    if absences_non_justifiees > 0:
        alertes.append({
            'type': 'info',
            'titre': 'Absences non justifiées',
            'message': f'{absences_non_justifiees} absence(s) enseignant non justifiée(s) ce mois',
            'lien': '/enseignants/presences'
        })
    
    return render_template('dashboard/index.html',
                         stats=stats,
                         activites=activites,
                         alertes=alertes)


@dashboard_bp.route('/statistiques/enseignants')
@login_required
@admin_required
def stats_enseignants():
    """Statistiques détaillées des enseignants"""
    
    # Répartition par grade
    repartition_grade = db.session.query(
        Enseignant.grade,
        func.count(Enseignant.id)
    ).filter_by(statut='actif').group_by(Enseignant.grade).all()
    
    # Répartition par département
    repartition_dept = db.session.query(
        Enseignant.departement_id,
        func.count(Enseignant.id)
    ).filter_by(statut='actif').group_by(Enseignant.departement_id).all()
    
    # Charge horaire
    enseignants = Enseignant.query.filter_by(statut='actif').all()
    charges_horaires = {
        'optimal': len([e for e in enseignants if 0.8 <= e.charge_horaire_pourcent/100 <= 1.0]),
        'surcharge': len([e for e in enseignants if e.charge_horaire_pourcent/100 > 1.0]),
        'sous_charge': len([e for e in enseignants if e.charge_horaire_pourcent/100 < 0.8])
    }
    
    # Taux de présence moyen
    presences_stats = db.session.query(
        func.count(PresenceEnseignant.id).label('total'),
        func.sum(func.case((PresenceEnseignant.statut == 'present', 1), else_=0)).label('presences')
    ).first()
    
    taux_presence_moyen = 0
    if presences_stats.total > 0:
        taux_presence_moyen = round((presences_stats.presences / presences_stats.total) * 100, 2)
    
    return render_template('dashboard/stats_enseignants.html',
                         repartition_grade=repartition_grade,
                         repartition_dept=repartition_dept,
                         charges_horaires=charges_horaires,
                         taux_presence_moyen=taux_presence_moyen)


@dashboard_bp.route('/statistiques/academique')
@login_required
@admin_required
def stats_academique():
    """Statistiques académiques"""
    
    # Notes par UE
    moyennes_ues = db.session.query(
        UniteEnseignement.intitule,
        func.avg(Note.note).label('moyenne'),
        func.count(Note.id).label('nb_notes')
    ).join(Evaluation).join(Note).filter(
        Note.note.isnot(None)
    ).group_by(UniteEnseignement.id).all()
    
    # Taux de réussite
    notes_totales = Note.query.filter(Note.note.isnot(None)).count()
    notes_reussies = Note.query.filter(Note.note >= 10).count()
    taux_reussite = round((notes_reussies / notes_totales * 100), 2) if notes_totales > 0 else 0
    
    # Répartition des mentions
    mentions = db.session.query(
        ReleveNotes.mention,
        func.count(ReleveNotes.id)
    ).filter(ReleveNotes.mention.isnot(None)).group_by(ReleveNotes.mention).all()
    
    # Évolution des inscriptions
    inscriptions_par_niveau = db.session.query(
        Classe.niveau,
        func.count(Classe.id)
    ).filter_by(est_active=True).group_by(Classe.niveau).all()
    
    return render_template('dashboard/stats_academique.html',
                         moyennes_ues=moyennes_ues,
                         taux_reussite=taux_reussite,
                         mentions=mentions,
                         inscriptions_par_niveau=inscriptions_par_niveau)


@dashboard_bp.route('/rapports')
@login_required
@permission_required(Permission.GENERATE_REPORTS)
def rapports():
    """Page de génération de rapports"""
    return render_template('dashboard/rapports.html')


@dashboard_bp.route('/rapports/generer', methods=['POST'])
@login_required
@permission_required(Permission.GENERATE_REPORTS)
def generer_rapport():
    """Générer un rapport personnalisé"""
    type_rapport = request.form.get('type_rapport')
    date_debut = request.form.get('date_debut')
    date_fin = request.form.get('date_fin')
    
    # À implémenter: génération de rapports PDF/Excel
    
    return jsonify({'status': 'success', 'message': 'Rapport en cours de génération'})


# ===== API pour graphiques =====

@dashboard_bp.route('/api/charts/charge-horaire')
@login_required
@admin_required
def api_chart_charge_horaire():
    """Données pour graphique charge horaire"""
    enseignants = Enseignant.query.filter_by(statut='actif').all()
    
    data = {
        'labels': [e.nom_complet for e in enseignants[:20]],  # Top 20
        'datasets': [{
            'label': 'Charge horaire (%)',
            'data': [e.charge_horaire_pourcent for e in enseignants[:20]],
            'backgroundColor': [
                'rgba(75, 192, 192, 0.6)' if e.charge_horaire_pourcent <= 100 
                else 'rgba(255, 99, 132, 0.6)' 
                for e in enseignants[:20]
            ]
        }]
    }
    
    return jsonify(data)


@dashboard_bp.route('/api/charts/notes-distribution')
@login_required
@admin_required
def api_chart_notes_distribution():
    """Distribution des notes"""
    
    # Regrouper par tranches
    tranches = {
        '0-5': Note.query.filter(Note.note < 5).count(),
        '5-10': Note.query.filter(and_(Note.note >= 5, Note.note < 10)).count(),
        '10-12': Note.query.filter(and_(Note.note >= 10, Note.note < 12)).count(),
        '12-14': Note.query.filter(and_(Note.note >= 12, Note.note < 14)).count(),
        '14-16': Note.query.filter(and_(Note.note >= 14, Note.note < 16)).count(),
        '16-20': Note.query.filter(Note.note >= 16).count()
    }
    
    data = {
        'labels': list(tranches.keys()),
        'datasets': [{
            'label': 'Nombre d\'étudiants',
            'data': list(tranches.values()),
            'backgroundColor': [
                'rgba(255, 99, 132, 0.6)',
                'rgba(255, 159, 64, 0.6)',
                'rgba(255, 205, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(153, 102, 255, 0.6)'
            ]
        }]
    }
    
    return jsonify(data)


@dashboard_bp.route('/api/charts/presences-mensuelles')
@login_required
@admin_required
def api_chart_presences_mensuelles():
    """Évolution mensuelle des présences"""
    
    # 6 derniers mois
    mois_data = []
    labels = []
    
    for i in range(6):
        date_mois = date.today() - timedelta(days=30*i)
        mois = date_mois.strftime('%B %Y')
        labels.insert(0, mois)
        
        presences = PresenceEnseignant.query.filter(
            extract('month', PresenceEnseignant.date_seance) == date_mois.month,
            extract('year', PresenceEnseignant.date_seance) == date_mois.year
        ).count()
        
        mois_data.insert(0, presences)
    
    data = {
        'labels': labels,
        'datasets': [{
            'label': 'Nombre de séances',
            'data': mois_data,
            'borderColor': 'rgba(75, 192, 192, 1)',
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'fill': True
        }]
    }
    
    return jsonify(data)


@dashboard_bp.route('/api/stats/temps-reel')
@login_required
@admin_required
def api_stats_temps_reel():
    """Statistiques en temps réel"""
    
    aujourd_hui = date.today()
    
    stats = {
        'connexions_aujourdhui': User.query.filter(
            func.date(User.last_login) == aujourd_hui
        ).count(),
        'evaluations_aujourdhui': Evaluation.query.filter(
            func.date(Evaluation.date_creation) == aujourd_hui
        ).count(),
        'notifications_envoyees': Notification.query.filter(
            func.date(Notification.date_creation) == aujourd_hui
        ).count(),
        'seances_aujourdhui': SeanceCours.query.filter_by(
            date_seance=aujourd_hui
        ).count()
    }
    
    return jsonify(stats)
