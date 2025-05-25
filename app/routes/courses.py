

from flask import Blueprint,current_app ,render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
import os
from datetime import datetime
from ..models.courses import Cours, Ressource, Professeur

# Création du Blueprint
coursesbp = Blueprint('courses', __name__, url_prefix='/courses')

# Configuration pour les uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'cours')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'zip'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@coursesbp.route('/')
@login_required
def courses():
    try:
        # Debug - Vérifiez ce qui est réellement récupéré
        print(f"Rôle utilisateur: {current_user.role}")
        
        if current_user.role == 'administrateur':
            cours = Cours.query.all()
            print("Mode administrateur - Tous les cours chargés")
        else:
            print(f"Filtrage pour - Cycle:{current_user.cycle}, Année:{current_user.annee}, Département:{current_user.departement}")
            cours = Cours.query.filter_by(
                cycle=current_user.cycle,
                annee=current_user.annee,
                departement=current_user.departement
            ).all()
        
        print(f"Nombre de cours trouvés: {len(cours)}")
        
        current_date = datetime.now().strftime("%d/%m/%Y")
        return render_template('PageCours.html', 
                            cours_list=cours,  
                            current_date=current_date)
    
    except Exception as e:
        print(f"ERREUR dans la route courses(): {str(e)}")
        flash("Une erreur est survenue lors du chargement des cours", "danger")
        return redirect(url_for('main.Page_Accueil'))
    
@coursesbp.route('/ressources/<int:cours_id>')
@login_required
def ressources_cours(cours_id):
    cours = Cours.query.get_or_404(cours_id)
    ressources = Ressource.query.filter_by(cours_id=cours_id).all()
    return render_template('courses/ressources.html',
                        cours=cours,
                        ressources=ressources)

@coursesbp.route('/telecharger/<int:cours_id>')
@login_required
def telecharger_cours(cours_id):
    try:
        # Récupérer le cours depuis la base de données
        cours = Cours.query.get_or_404(cours_id)
        
        # Chemin complet du fichier
        file_path = os.path.join(UPLOAD_FOLDER, cours.fichier)
        
        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            flash("Le fichier demandé n'existe pas sur le serveur", "danger")
            return redirect(url_for('courses.courses'))
            
        # Envoyer le fichier
        return send_from_directory(
            directory=UPLOAD_FOLDER,
            path=cours.fichier,
            as_attachment=True,
            download_name=f"{cours.code}_{cours.titre}.{cours.fichier.split('.')[-1]}"
        )
    except Exception as e:
        current_app.logger.error(f"Erreur de téléchargement: {str(e)}")
        flash("Une erreur est survenue lors du téléchargement", "danger")
        return redirect(url_for('courses.courses'))


@coursesbp.route('/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_cours():
    if current_user.role != 'administrateur':
        flash('Accès refusé', 'danger')
        return redirect(url_for('courses.courses'))
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        code = request.form['code']
        titre = request.form['titre']
        description = request.form['description']
        credits = int(request.form['credits'])
        cycle = request.form['cycle']
        annee = int(request.form['annee'])
        departement = request.form['departement']
        parcours = request.form.get('parcours', None)
        semestre = int(request.form['semestre'])
        specialisation = request.form.get('specialisation', None)
        horaire = request.form['horaire']
        lieu = request.form['lieu']
        professeur_id = int(request.form['professeur'])
        
        # Gestion du fichier
        if 'fichier' not in request.files:
            flash('Aucun fichier sélectionné', 'danger')
            return redirect(request.url)
        
        file = request.files['fichier']
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{code}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            
            # Créer le cours
            nouveau_cours = Cours(
                code=code,
                titre=titre,
                description=description,
                credits=credits,
                cycle=cycle,
                annee=annee,
                departement=departement,
                parcours=parcours,
                semestre=semestre,
                specialisation=specialisation,
                horaire=horaire,
                lieu=lieu,
                fichier=filename,
                professeur_id=professeur_id
            )
            
            db.session.add(nouveau_cours)
            db.session.commit()
            flash('Cours ajouté avec succès', 'success')
            return redirect(url_for('courses.courses'))
    
    # Pour GET: afficher le formulaire
    professeurs = Professeur.query.all()
    return render_template('courses/ajouter_cours.html', professeurs=professeurs)



@coursesbp.route('/modifier/<int:cours_id>', methods=['GET', 'POST'])
@login_required
def modifier_cours(cours_id):
    if current_user.role != 'administrateur':
        flash('Accès refusé', 'danger')
        return redirect(url_for('courses.courses'))
    
    cours = Cours.query.get_or_404(cours_id)
    
    if request.method == 'POST':
        # Mise à jour des données
        cours.code = request.form['code']
        cours.titre = request.form['titre']
        cours.description = request.form['description']
        cours.credits = int(request.form['credits'])
        cours.cycle = request.form['cycle']
        cours.annee = int(request.form['annee'])
        cours.departement = request.form['departement']
        cours.parcours = request.form.get('parcours', None)
        cours.semestre = int(request.form['semestre'])
        cours.specialisation = request.form.get('specialisation', None)
        cours.horaire = request.form['horaire']
        cours.lieu = request.form['lieu']
        cours.professeur_id = int(request.form['professeur'])
        
        # Gestion du fichier si un nouveau est uploadé
        if 'fichier' in request.files:
            file = request.files['fichier']
            if file.filename != '' and allowed_file(file.filename):
                # Supprimer l'ancien fichier
                if cours.fichier:
                    try:
                        os.remove(os.path.join(UPLOAD_FOLDER, cours.fichier))
                    except OSError:
                        pass
                
                # Sauvegarder le nouveau
                filename = secure_filename(f"{cours.code}_{file.filename}")
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                cours.fichier = filename
        
        db.session.commit()
        flash('Cours mis à jour avec succès', 'success')
        return redirect(url_for('courses.mes_cours'))
    
    professeurs = Professeur.query.all()
    return render_template('courses/modifier_cours.html', cours=cours, professeurs=professeurs)

@coursesbp.route('/supprimer/<int:cours_id>')
@login_required
def supprimer_cours(cours_id):
    if current_user.role != 'administrateur':
        flash('Accès refusé', 'danger')
        return redirect(url_for('courses.mes_cours'))
    
    cours = Cours.query.get_or_404(cours_id)
    
    # Supprimer le fichier associé
    if cours.fichier:
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, cours.fichier))
        except OSError:
            pass
    
    db.session.delete(cours)
    db.session.commit()
    flash('Cours supprimé avec succès', 'success')
    return redirect(url_for('courses.courses'))

'''# Fonction pour enregistrer le blueprint dans l'application
def init_app(app):
    app.config['COURSES_UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.register_blueprint(coursesbp)'''