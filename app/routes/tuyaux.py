from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
import os
from datetime import datetime
from ..models.tuyaux import Tuyau
from ..models.Users import User  

# Création du Blueprint
tuyauxbp = Blueprint('tuyaux', __name__, url_prefix='/tuyaux')

# Configuration pour les uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'tuyaux')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@tuyauxbp.route('/')
@login_required
def PageTuyaux():
    try:
        # Récupérer le nombre de téléchargements aujourd'hui pour l'utilisateur
        downloads_today = 0  # À implémenter selon votre système de suivi
        
        # Récupérer tous les tuyaux
        tuyaux = Tuyau.query.order_by(Tuyau.date_ajout.desc()).all()
        
        current_date = datetime.now().strftime("%d/%m/%Y")
        return render_template('PageTuyaux.html', 
                            tuyaux_list=tuyaux,
                            downloads_today=downloads_today,
                            current_date=current_date)
    
    except Exception as e:
        current_app.logger.error(f"Erreur dans la route PageTuyaux: {str(e)}")
        flash("Une erreur est survenue lors du chargement des tuyaux", "danger")
        return redirect(url_for('principale.Page_Principale'))

@tuyauxbp.route('/telecharger/<int:tuyau_id>')
@login_required
def telecharger_tuyau(tuyau_id):
    try:
        # Vérifier la limite de téléchargement
        downloads_today = 0  # À implémenter
        if downloads_today >= 3:
            flash("Vous avez atteint votre limite de téléchargements pour aujourd'hui (3 max)", "warning")
            return redirect(url_for('tuyaux.PageTuyaux'))
        
        # Récupérer le tuyau
        tuyau = Tuyau.query.get_or_404(tuyau_id)
        
        # Chemin complet du fichier
        file_path = os.path.join(UPLOAD_FOLDER, tuyau.fichier)
        
        if not os.path.exists(file_path):
            flash("Le fichier demandé n'existe pas sur le serveur", "danger")
            return redirect(url_for('tuyaux.PageTuyaux'))
            
        # Incrémenter le compteur de téléchargements (à implémenter)
        
        # Envoyer le fichier
        return send_from_directory(
            directory=UPLOAD_FOLDER,
            path=tuyau.fichier,
            as_attachment=True,
            download_name=f"{tuyau.titre}.{tuyau.fichier.split('.')[-1]}"
        )
    except Exception as e:
        current_app.logger.error(f"Erreur de téléchargement: {str(e)}")
        flash("Une erreur est survenue lors du téléchargement", "danger")
        return redirect(url_for('tuyaux.PageTuyaux'))

@tuyauxbp.route('/ajouter', methods=['POST'])
@login_required
def ajouter_tuyau():
    try:
        if request.method == 'POST':
            # Récupérer les données du formulaire
            titre = request.form['titre']
            description = request.form['description']
            matiere = request.form['matiere']
            cycle = request.form['cycle']
            niveau = request.form['niveau']
            departement = request.form['departement']
            semestre = request.form['semestre']
            annee_academique = request.form['annee_academique']
            
            # Gestion du fichier
            if 'fichier' not in request.files:
                flash('Aucun fichier sélectionné', 'danger')
                return redirect(url_for('tuyaux.PageTuyaux'))
            
            file = request.files['fichier']
            if file.filename == '':
                flash('Aucun fichier sélectionné', 'danger')
                return redirect(url_for('tuyaux.PageTuyaux'))
            
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{current_user.id}_{datetime.now().timestamp()}_{file.filename}")
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                
                # Créer le tuyau
                nouveau_tuyau = Tuyau(
                    titre=titre,
                    description=description,
                    matiere=matiere,
                    cycle=cycle,
                    niveau=niveau,
                    departement=departement,
                    semestre=semestre,
                    annee_academique=annee_academique,
                    type_fichier=file.filename.split('.')[-1],
                    fichier=filename,
                    utilisateur_id=current_user.id
                )
                
                db.session.add(nouveau_tuyau)
                db.session.commit()
                flash('Tuyau ajouté avec succès', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de l'ajout du tuyau: {str(e)}")
        flash("Une erreur est survenue lors de l'ajout du tuyau", "danger")
    
    return redirect(url_for('tuyaux.PageTuyaux'))

@tuyauxbp.route('/modifier/<int:tuyau_id>', methods=['POST'])
@login_required
def modifier_tuyau(tuyau_id):
    try:
        tuyau = Tuyau.query.get_or_404(tuyau_id)
        
        # Vérifier que l'utilisateur est admin ou l'auteur
        if current_user.role != 'admin' and current_user.id != tuyau.utilisateur_id:
            flash('Accès refusé', 'danger')
            return redirect(url_for('tuyaux.PageTuyaux'))
        
        # Mise à jour des données
        tuyau.titre = request.form['titre']
        tuyau.description = request.form['description']
        tuyau.matiere = request.form['matiere']
        tuyau.cycle = request.form['cycle']
        tuyau.niveau = request.form['niveau']
        tuyau.departement = request.form['departement']
        tuyau.semestre = request.form['semestre']
        tuyau.annee_academique = request.form['annee_academique']
        
        # Gestion du fichier si un nouveau est uploadé
        if 'fichier' in request.files:
            file = request.files['fichier']
            if file.filename != '' and allowed_file(file.filename):
                # Supprimer l'ancien fichier
                if tuyau.fichier:
                    try:
                        os.remove(os.path.join(UPLOAD_FOLDER, tuyau.fichier))
                    except OSError:
                        pass
                
                # Sauvegarder le nouveau
                filename = secure_filename(f"{current_user.id}_{datetime.now().timestamp()}_{file.filename}")
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                tuyau.fichier = filename
                tuyau.type_fichier = file.filename.split('.')[-1]
        
        db.session.commit()
        flash('Tuyau mis à jour avec succès', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la modification du tuyau: {str(e)}")
        flash("Une erreur est survenue lors de la modification du tuyau", "danger")
    
    return redirect(url_for('tuyaux.PageTuyaux'))

@tuyauxbp.route('/supprimer/<int:tuyau_id>')
@login_required
def supprimer_tuyau(tuyau_id):
    try:
        tuyau = Tuyau.query.get_or_404(tuyau_id)
        
        # Vérifier que l'utilisateur est admin ou l'auteur
        if current_user.role != 'admin' and current_user.id != tuyau.utilisateur_id:
            flash('Accès refusé', 'danger')
            return redirect(url_for('tuyaux.PageTuyaux'))
        
        # Supprimer le fichier associé
        if tuyau.fichier:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, tuyau.fichier))
            except OSError:
                pass
        
        db.session.delete(tuyau)
        db.session.commit()
        flash('Tuyau supprimé avec succès', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la suppression du tuyau: {str(e)}")
        flash("Une erreur est survenue lors de la suppression du tuyau", "danger")
    
    return redirect(url_for('tuyaux.PageTuyaux'))