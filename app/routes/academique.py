"""
Routes pour la gestion académique
Programmes, évaluations, notes, emplois du temps
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app.extensions import db
from app.models.academique import (
    UniteEnseignement, ElementConstitutif, Filiere, Classe,
    Evaluation, Note, ReleveNotes, Salle, SeanceCours, InscriptionClasse
)
from app.models.enseignants import Enseignant
from app.models.notifications import Notification
from app.permissions import (
    Permission, permission_required, enseignant_or_admin_required,
    can_manage_evaluation
)
from sqlalchemy import func, and_, or_
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

academique_bp = Blueprint('academique', __name__, url_prefix='/academique')


# ===== GESTION DES UNITÉS D'ENSEIGNEMENT =====

@academique_bp.route('/unites-enseignement')
@login_required
@enseignant_or_admin_required
def liste_ues():
    """Liste des unités d'enseignement"""
    page = request.args.get('page', 1, type=int)
    niveau = request.args.get('niveau', '')
    filiere_id = request.args.get('filiere', type=int)
    search = request.args.get('search', '')
    
    query = UniteEnseignement.query.filter_by(est_active=True)
    
    if niveau:
        query = query.filter_by(niveau=niveau)
    if filiere_id:
        query = query.filter_by(filiere_id=filiere_id)
    if search:
        query = query.filter(
            or_(
                UniteEnseignement.code.ilike(f'%{search}%'),
                UniteEnseignement.intitule.ilike(f'%{search}%')
            )
        )
    
    ues = query.order_by(UniteEnseignement.niveau, UniteEnseignement.semestre).paginate(
        page=page, per_page=20, error_out=False
    )
    
    filieres = Filiere.query.filter_by(est_active=True).all()
    
    return render_template('academique/ues/liste.html', ues=ues, filieres=filieres)


@academique_bp.route('/unites-enseignement/nouveau', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MANAGE_COURSES)
def nouvelle_ue():
    """Créer une nouvelle UE"""
    if request.method == 'POST':
        try:
            ue = UniteEnseignement(
                code=request.form.get('code'),
                intitule=request.form.get('intitule'),
                description=request.form.get('description'),
                credits=request.form.get('credits', type=int),
                coefficient=request.form.get('coefficient', type=float),
                cycle=request.form.get('cycle'),
                niveau=request.form.get('niveau'),
                semestre=request.form.get('semestre', type=int),
                filiere_id=request.form.get('filiere_id', type=int),
                volume_cm=request.form.get('volume_cm', type=int, default=0),
                volume_td=request.form.get('volume_td', type=int, default=0),
                volume_tp=request.form.get('volume_tp', type=int, default=0),
                type_ue=request.form.get('type_ue'),
                nature=request.form.get('nature'),
                annee_academique=request.form.get('annee_academique'),
                est_capitalizable=request.form.get('est_capitalizable') == 'on',
                est_active=True
            )
            
            db.session.add(ue)
            db.session.commit()
            
            flash(f'UE "{ue.intitule}" créée avec succès', 'success')
            return redirect(url_for('academique.detail_ue', id=ue.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')
    
    filieres = Filiere.query.filter_by(est_active=True).all()
    return render_template('academique/ues/formulaire.html', filieres=filieres, action='Créer')


@academique_bp.route('/unites-enseignement/<int:id>')
@login_required
@enseignant_or_admin_required
def detail_ue(id):
    """Détail d'une UE"""
    ue = UniteEnseignement.query.get_or_404(id)
    
    # Éléments constitutifs
    elements = ue.elements_constitutifs.all()
    
    # Affectations enseignants
    affectations = ue.affectations.filter_by(est_active=True).all()
    
    # Évaluations
    evaluations = ue.evaluations.order_by(Evaluation.date_evaluation.desc()).limit(10).all()
    
    return render_template('academique/ues/detail.html',
                         ue=ue,
                         elements=elements,
                         affectations=affectations,
                         evaluations=evaluations)


# ===== GESTION DES ÉVALUATIONS ET NOTES =====

@academique_bp.route('/evaluations')
@login_required
@permission_required(Permission.MANAGE_EVALUATIONS)
def liste_evaluations():
    """Liste des évaluations"""
    page = request.args.get('page', 1, type=int)
    classe_id = request.args.get('classe', type=int)
    ue_id = request.args.get('ue', type=int)
    
    query = Evaluation.query
    
    # Si enseignant, ne montrer que ses évaluations
    if current_user.role == 'enseignant':
        ues_enseignees = [aff.unite_enseignement_id for aff in current_user.enseignant.affectations if aff.est_active]
        query = query.filter(Evaluation.ue_id.in_(ues_enseignees))
    
    if classe_id:
        query = query.filter_by(classe_id=classe_id)
    if ue_id:
        query = query.filter_by(ue_id=ue_id)
    
    evaluations = query.order_by(Evaluation.date_evaluation.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    classes = Classe.query.filter_by(est_active=True).all()
    ues = UniteEnseignement.query.filter_by(est_active=True).all()
    
    return render_template('academique/evaluations/liste.html',
                         evaluations=evaluations,
                         classes=classes,
                         ues=ues)


@academique_bp.route('/evaluations/nouvelle', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MANAGE_EVALUATIONS)
def nouvelle_evaluation():
    """Créer une nouvelle évaluation"""
    if request.method == 'POST':
        try:
            evaluation = Evaluation(
                titre=request.form.get('titre'),
                description=request.form.get('description'),
                ue_id=request.form.get('ue_id', type=int),
                classe_id=request.form.get('classe_id', type=int),
                type_evaluation=request.form.get('type_evaluation'),
                session=request.form.get('session'),
                coefficient=request.form.get('coefficient', type=float),
                note_max=request.form.get('note_max', type=float, default=20.0),
                date_evaluation=datetime.strptime(request.form.get('date_evaluation'), '%Y-%m-%dT%H:%M') if request.form.get('date_evaluation') else None,
                duree_minutes=request.form.get('duree_minutes', type=int),
                salle=request.form.get('salle'),
                annee_academique=request.form.get('annee_academique'),
                semestre=request.form.get('semestre', type=int),
                creee_par_id=current_user.id
            )
            
            db.session.add(evaluation)
            db.session.commit()
            
            # Créer les entrées de notes pour tous les étudiants de la classe
            inscriptions = InscriptionClasse.query.filter_by(
                classe_id=evaluation.classe_id,
                est_active=True
            ).all()
            
            for inscription in inscriptions:
                note = Note(
                    evaluation_id=evaluation.id,
                    etudiant_id=inscription.etudiant_id,
                    saisie_par_id=current_user.id
                )
                db.session.add(note)
            
            db.session.commit()
            
            flash(f'Évaluation "{evaluation.titre}" créée avec succès', 'success')
            return redirect(url_for('academique.saisie_notes', eval_id=evaluation.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')
    
    classes = Classe.query.filter_by(est_active=True).all()
    ues = UniteEnseignement.query.filter_by(est_active=True).all()
    
    return render_template('academique/evaluations/formulaire.html',
                         classes=classes,
                         ues=ues,
                         action='Créer')


@academique_bp.route('/evaluations/<int:eval_id>/notes', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MANAGE_GRADES)
def saisie_notes(eval_id):
    """Saisir/modifier les notes d'une évaluation"""
    evaluation = Evaluation.query.get_or_404(eval_id)
    
    # Vérifier permissions fines pour les enseignants
    if current_user.role == 'enseignant' and not can_manage_evaluation(evaluation):
        flash('Vous n\'êtes pas autorisé à saisir les notes de cette évaluation', 'danger')
        return redirect(url_for('academique.liste_evaluations'))
    
    if request.method == 'POST':
        try:
            notes_data = request.form.to_dict()
            
            for key, value in notes_data.items():
                if key.startswith('note_'):
                    note_id = int(key.split('_')[1])
                    note = Note.query.get(note_id)
                    
                    if note and note.evaluation_id == eval_id:
                        # Gérer absence
                        est_absent = f'absent_{note_id}' in notes_data
                        
                        if est_absent:
                            note.est_absent = True
                            note.note = None
                        else:
                            note.est_absent = False
                            if value:
                                note.note = float(value)
                        
                        note.saisie_par_id = current_user.id
                        note.date_modification = datetime.utcnow()
            
            db.session.commit()
            flash('Notes enregistrées avec succès', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la saisie: {str(e)}', 'danger')
    
    # Charger les notes
    notes = evaluation.notes.join(Note.etudiant).order_by('utilisateurs.nom', 'utilisateurs.prenom').all()
    
    # Statistiques
    notes_saisies = [n for n in notes if n.note is not None and not n.est_absent]
    stats = {}
    if notes_saisies:
        valeurs = [n.note for n in notes_saisies]
        stats = {
            'moyenne': round(sum(valeurs) / len(valeurs), 2),
            'min': min(valeurs),
            'max': max(valeurs),
            'saisies': len(notes_saisies),
            'total': len(notes),
            'absents': len([n for n in notes if n.est_absent])
        }
    
    return render_template('academique/evaluations/saisie_notes.html',
                         evaluation=evaluation,
                         notes=notes,
                         stats=stats)


@academique_bp.route('/evaluations/<int:eval_id>/publier', methods=['POST'])
@login_required
@permission_required(Permission.MANAGE_GRADES)
def publier_notes(eval_id):
    """Publier les résultats d'une évaluation"""
    evaluation = Evaluation.query.get_or_404(eval_id)
    
    if current_user.role == 'enseignant' and not can_manage_evaluation(evaluation):
        flash('Accès non autorisé pour cette évaluation', 'danger')
        return redirect(url_for('academique.liste_evaluations'))
    
    try:
        evaluation.est_publiee = True
        evaluation.date_publication = datetime.utcnow()
        
        # Notifier les étudiants
        notes = evaluation.notes.filter(Note.note.isnot(None)).all()
        for note in notes:
            Notification.notifier_resultats(
                etudiant_id=note.etudiant_id,
                evaluation_titre=evaluation.titre,
                note=note.note
            )
        
        db.session.commit()
        flash(f'Résultats publiés! {len(notes)} étudiants notifiés.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur: {str(e)}', 'danger')
    
    return redirect(url_for('academique.saisie_notes', eval_id=eval_id))


@academique_bp.route('/resultats')
@login_required
def mes_resultats():
    """Consultation des résultats par l'étudiant"""
    if current_user.role != 'etudiant':
        flash('Accès réservé aux étudiants', 'danger')
        return redirect(url_for('main.Page_Accueil'))
    
    # Charger les notes de l'étudiant
    notes = Note.query.join(Evaluation).filter(
        Note.etudiant_id == current_user.id,
        Evaluation.est_publiee == True
    ).order_by(Evaluation.date_evaluation.desc()).all()
    
    # Regrouper par UE
    notes_par_ue = {}
    for note in notes:
        ue_id = note.evaluation.ue_id
        if ue_id not in notes_par_ue:
            notes_par_ue[ue_id] = {
                'ue': note.evaluation.unite_enseignement,
                'notes': []
            }
        notes_par_ue[ue_id]['notes'].append(note)
    
    return render_template('academique/resultats/consultation.html',
                         notes_par_ue=notes_par_ue)


@academique_bp.route('/releves/<int:etudiant_id>/<annee>/<int:semestre>')
@login_required
def releve_notes(etudiant_id, annee, semestre):
    """Génération du relevé de notes"""
    # Vérifier permissions
    if current_user.role == 'etudiant' and current_user.id != etudiant_id:
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('main.Page_Accueil'))
    
    releve = ReleveNotes.query.filter_by(
        etudiant_id=etudiant_id,
        annee_academique=annee,
        semestre=semestre
    ).first()
    
    if not releve:
        flash('Relevé de notes non trouvé', 'warning')
        return redirect(url_for('academique.mes_resultats'))
    
    return render_template('academique/resultats/releve.html', releve=releve)


@academique_bp.route('/releves/<int:releve_id>/pdf')
@login_required
def releve_pdf(releve_id):
    """Télécharger le relevé en PDF"""
    releve = ReleveNotes.query.get_or_404(releve_id)
    
    # Vérifier permissions
    if current_user.role == 'etudiant' and current_user.id != releve.etudiant_id:
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('main.Page_Accueil'))
    
    # Générer PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # En-tête
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "RELEVÉ DE NOTES")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 770, f"Étudiant: {releve.etudiant.nom_complet}")
    p.drawString(100, 750, f"Année: {releve.annee_academique} - Semestre {releve.semestre}")
    p.drawString(100, 730, f"Moyenne générale: {releve.moyenne_generale}/20")
    p.drawString(100, 710, f"Crédits obtenus: {releve.credits_obtenus}/{releve.credits_totaux}")
    
    if releve.mention:
        p.drawString(100, 690, f"Mention: {releve.mention.upper()}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'releve_{releve.etudiant.username}_{releve.annee_academique}_S{releve.semestre}.pdf',
        mimetype='application/pdf'
    )


# ===== EMPLOIS DU TEMPS =====

@academique_bp.route('/emplois-du-temps')
@login_required
def emplois_du_temps():
    """Consulter les emplois du temps"""
    if current_user.role == 'etudiant':
        # Trouver la classe de l'étudiant
        inscription = InscriptionClasse.query.filter_by(
            etudiant_id=current_user.id,
            est_active=True
        ).first()
        
        if not inscription:
            flash('Vous n\'êtes inscrit à aucune classe', 'warning')
            return redirect(url_for('principale.Page_Principale'))
        
        return redirect(url_for('academique.emploi_classe', classe_id=inscription.classe_id))
    
    elif current_user.role == 'enseignant':
        return redirect(url_for('academique.emploi_enseignant', ens_id=current_user.enseignant.id))
    
    else:
        # Admin: vue globale
        classes = Classe.query.filter_by(est_active=True).all()
        return render_template('academique/emplois_temps/selection.html', classes=classes)


@academique_bp.route('/emplois-du-temps/classe/<int:classe_id>')
@login_required
def emploi_classe(classe_id):
    """Emploi du temps d'une classe"""
    classe = Classe.query.get_or_404(classe_id)
    
    # Date de la semaine
    semaine = request.args.get('semaine', date.today().strftime('%Y-%W'))
    
    # Charger les séances de la semaine
    seances = SeanceCours.query.filter_by(classe_id=classe_id).order_by(
        SeanceCours.date_seance, SeanceCours.heure_debut
    ).all()
    
    # Organiser par jour
    emploi_du_temps = {}
    for seance in seances:
        jour = seance.date_seance.strftime('%A')
        if jour not in emploi_du_temps:
            emploi_du_temps[jour] = []
        emploi_du_temps[jour].append(seance)
    
    return render_template('academique/emplois_temps/classe.html',
                         classe=classe,
                         emploi_du_temps=emploi_du_temps,
                         semaine=semaine)


@academique_bp.route('/emplois-du-temps/enseignant/<int:ens_id>')
@login_required
def emploi_enseignant(ens_id):
    """Emploi du temps d'un enseignant"""
    enseignant = Enseignant.query.get_or_404(ens_id)
    
    # Vérifier permissions
    if current_user.role == 'enseignant' and current_user.enseignant.id != ens_id:
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('main.Page_Accueil'))
    
    # Charger les séances
    seances = enseignant.seances.order_by(
        SeanceCours.date_seance, SeanceCours.heure_debut
    ).all()
    
    # Organiser par jour
    emploi_du_temps = {}
    for seance in seances:
        jour = seance.date_seance.strftime('%A')
        if jour not in emploi_du_temps:
            emploi_du_temps[jour] = []
        emploi_du_temps[jour].append(seance)
    
    return render_template('academique/emplois_temps/enseignant.html',
                         enseignant=enseignant,
                         emploi_du_temps=emploi_du_temps)


# ===== API =====

@academique_bp.route('/api/statistiques')
@login_required
@permission_required(Permission.VIEW_STATS)
def api_statistiques():
    """API statistiques académiques"""
    
    stats = {
        'ues': UniteEnseignement.query.filter_by(est_active=True).count(),
        'classes': Classe.query.filter_by(est_active=True).count(),
        'evaluations': Evaluation.query.count(),
        'notes_saisies': Note.query.filter(Note.note.isnot(None)).count()
    }
    
    return jsonify(stats)
