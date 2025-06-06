from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from datetime import datetime
from ..models.actualites import Actualite, Commentaire, CategorieActualite, PieceJointe, Departement, Pays
from ..extensions import db
from .forms import ActualiteForm, CommentaireForm
from werkzeug.utils import secure_filename
import os

actualites_bp = Blueprint('actualites', __name__, template_folder='templates')

# Configuration pour le téléchargement des fichiers
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
UPLOAD_FOLDER = 'static/uploads/actualites'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Helper function to save uploaded files"""
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
        # Créer le dossier s'il n'existe pas
        upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        return url_for('static', filename=f'uploads/actualites/{filename}')
    return None

def delete_associated_files(actualite):
    """Helper function to delete files associated with an actualite"""
    if actualite.image_url:
        try:
            # Extraire le chemin relatif depuis l'URL
            relative_path = actualite.image_url.replace('/static/', '')
            file_path = os.path.join(current_app.root_path, 'static', relative_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass
    
    for piece in actualite.pieces_jointes:
        try:
            relative_path = piece.url.replace('/static/', '')
            file_path = os.path.join(current_app.root_path, 'static', relative_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass

# ========================
# PUBLIC ROUTES
# ========================

@actualites_bp.route('/actualites')
def liste_actualites():
    """Liste des actualités publiques, filtrées par catégorie et type_actualite"""
    categorie = request.args.get('categorie')
    type_actualite = request.args.get('type_actualite')  # Ajout du filtre type
    page = request.args.get('page', 1, type=int)
    per_page = 6

    # Base query
    query = Actualite.query.filter_by(statut='publie').order_by(Actualite.date_publication.desc())

    if categorie:
        query = query.filter_by(categorie=categorie)
    if type_actualite:
        query = query.filter_by(type_actualite=type_actualite)

    actualites = query.paginate(page=page, per_page=per_page, error_out=False)

    # Récupérer les catégories avec leur compte
    categories_result = db.session.query(
        Actualite.categorie, 
        db.func.count(Actualite.id).label('count')
    ).filter(
        Actualite.categorie.isnot(None),
        Actualite.statut == 'publie'
    ).group_by(Actualite.categorie).all()
    categories = [(cat.categorie, cat.count) for cat in categories_result if cat.categorie]

    # Récupérer les types d'actualités distincts pour le filtre
    types_result = db.session.query(Actualite.type_actualite).distinct().filter(Actualite.type_actualite.isnot(None)).all()
    types_actualite = [t[0] for t in types_result if t[0]]

    total_actualites = Actualite.query.filter_by(statut='publie').count()

    return render_template(
        'actualites/liste.html',
        actualites=actualites,
        categories=categories,
        types_actualite=types_actualite,
        current_categorie=categorie,
        current_type=type_actualite,
        total_actualites=total_actualites
    )
@actualites_bp.route('/actualites/<int:actualite_id>')

@actualites_bp.route('/actualites/<int:actualite_id>')
def detail_actualite(actualite_id):
    """Détail d'une actualité"""
    actualite = Actualite.query.get_or_404(actualite_id)
    
    if actualite.statut != 'publie' and (not current_user.is_authenticated or 
                                        (current_user.id != actualite.auteur_id and current_user.role != 'administrateur')):
        abort(404)
    
    actualite.incrementer_vues()
    form = CommentaireForm()
    
    commentaires = actualite.commentaires.filter_by(est_approuve=True).order_by(Commentaire.date_creation.desc()).all()
    actualites_similaires = Actualite.query.filter(
        Actualite.categorie == actualite.categorie,
        Actualite.id != actualite.id,
        Actualite.statut == 'publie'
    ).order_by(db.func.random()).limit(3).all()
    
    return render_template(
        'actualites/detail.html',
        actualite=actualite,
        comment_form=form,  # <-- nom attendu dans le template
        commentaires=commentaires,
        actualites_similaires=actualites_similaires
    )

@actualites_bp.route('/actualites/<int:actualite_id>/commenter', methods=['POST'])
@login_required
def commenter_actualite(actualite_id):
    """Ajouter un commentaire à une actualité"""
    actualite = Actualite.query.get_or_404(actualite_id)
    form = CommentaireForm()
    
    if form.validate_on_submit():
        nouveau_commentaire = Commentaire(
            contenu=form.contenu.data,
            auteur_id=current_user.id,
            actualite_id=actualite.id,
            est_approuve=current_user.role in ['administrateur', 'professeur']
        )
        db.session.add(nouveau_commentaire)
        db.session.commit()
        flash('Votre commentaire a été ajouté!', 'success')
    else:
        flash('Erreur dans le formulaire de commentaire.', 'danger')
    
    return redirect(url_for('actualites.detail_actualite', actualite_id=actualite.id))


# ========================
# AUTHOR ROUTES (Auteur + Admin)
# ========================

@actualites_bp.route('/actualites/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_actualite():
    """Ajouter une nouvelle actualité"""
    if current_user.role not in ['administrateur', 'professeur']:
        abort(403)
    
    form = ActualiteForm()

    # === ICI : Ajoute tes catégories et départements ===
    form.categorie.choices = [
        ('evenement', 'Événement'),
        ('conference', 'Conférence'),
        ('diplome', 'Diplôme'),
        ('partenariat', 'Partenariat'),
        ('autre', 'Autre')
        ]
    form.departement.choices = [
        ('', 'Sélectionnez un département'),
        ('info', 'Informatique'),
        ('genie_civil', 'Génie Civil'),
        ('electrique', 'Génie Électrique'),
        ('gestion', 'Gestion'),
        ('biologie', 'Biologie')
    ]

    

    if form.validate_on_submit():
        actualite = Actualite(
            titre=form.titre.data,
            slug=form.slug.data,
            contenu=form.contenu.data,
            resume=form.resume.data,
            categorie=form.categorie.data,
            sous_categorie=form.sous_categorie.data,
            image_alt=form.image_alt.data,
            date_evenement=form.date_evenement.data,
            lieu=form.lieu.data,
            auteur_id=current_user.id,
            statut=form.statut.data,
            est_important=form.est_important.data,
            mots_cles=form.mots_cles.data,
            meta_description=form.meta_description.data,
            type_actualite=form.type_actualite.data
        )
        
        # Gestion de l'image principale
        if form.image.data:
            image_url = save_uploaded_file(form.image.data)
            if image_url:
                actualite.image_url = image_url
        
        db.session.add(actualite)
        db.session.commit()
        
        # Gestion des pièces jointes
        if form.pieces_jointes.data:
            for piece in form.pieces_jointes.data:
                if piece.filename:  # Vérifier que le fichier n'est pas vide
                    piece_url = save_uploaded_file(piece)
                    if piece_url:
                        # Calculer la taille du fichier correctement
                        relative_path = piece_url.replace('/static/', '')
                        file_path = os.path.join(current_app.root_path, 'static', relative_path)
                        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                        
                        piece_jointe = PieceJointe(
                            nom=piece.filename,
                            url=piece_url,
                            type_fichier=piece.filename.rsplit('.', 1)[1].lower(),
                            taille=file_size,
                            actualite_id=actualite.id
                        )
                        db.session.add(piece_jointe)
            db.session.commit()
        
        flash('Actualité publiée avec succès!', 'success')
        return redirect(url_for('actualites.detail_actualite', actualite_id=actualite.id))
    
    elif request.method == 'POST' and not form.validate_on_submit():
        print(form.errors)
        flash('Erreur : Veuillez corriger les champs du formulaire.', 'danger')
    
    # Passer la liste des catégories si besoin dans le formulaire
    categories_result = db.session.query(Actualite.categorie).distinct().filter(Actualite.categorie.isnot(None)).all()
    categories = [cat[0] for cat in categories_result if cat[0]]
    
    return render_template('actualites/ajouter_actualite.html', form=form, categories=categories, actualite=None)

@actualites_bp.route('/actualites/<int:actualite_id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier_actualite(actualite_id):
    """Modifier une actualité existante"""
    actualite = Actualite.query.get_or_404(actualite_id)
    
    if current_user.id != actualite.auteur_id and current_user.role != 'administrateur':
        abort(403)
    
    form = ActualiteForm(obj=actualite)

    # === ICI : Ajoute tes catégories et départements ===
    form.categorie.choices = [
        ('evenement', 'Événement'),
        ('conference', 'Conférence'),
        ('diplome', 'Diplôme'),
        ('partenariat', 'Partenariat'),
        ('autre', 'Autre')
        ]
    form.departement.choices = [
        ('', 'Sélectionnez un Domaine'),
        ('info', 'Politique '),
        ('Statisti', 'Education'),
        ('electrique', 'Recherche et Innovation'),
        ('gestion', 'Sport et Loisirs'),
        ('biologie', 'Diversite et Environnement')
    ]
    
    if form.validate_on_submit():
        actualite.titre = form.titre.data
        actualite.slug = form.slug.data
        actualite.contenu = form.contenu.data
        actualite.resume = form.resume.data
        actualite.categorie = form.categorie.data
        actualite.sous_categorie = form.sous_categorie.data
        actualite.image_alt = form.image_alt.data
        actualite.date_evenement = form.date_evenement.data
        actualite.lieu = form.lieu.data
        actualite.statut = form.statut.data
        actualite.est_important = form.est_important.data
        actualite.mots_cles = form.mots_cles.data
        actualite.meta_description = form.meta_description.data
        
        # Gestion de l'image principale
        if form.image.data and form.image.data.filename:
            # Supprimer l'ancienne image si elle existe
            if actualite.image_url:
                try:
                    relative_path = actualite.image_url.replace('/static/', '')
                    old_file_path = os.path.join(current_app.root_path, 'static', relative_path)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                except OSError:
                    pass
            
            image_url = save_uploaded_file(form.image.data)
            if image_url:
                actualite.image_url = image_url
        
        db.session.commit()
        flash('Actualité mise à jour avec succès!', 'success')
        return redirect(url_for('actualites.detail_actualite', actualite_id=actualite.id))
    
    return render_template('actualites/modifier.html', form=form, actualite=actualite)

@actualites_bp.route('/actualites/<int:actualite_id>/supprimer', methods=['POST'])
@login_required
def supprimer_actualite(actualite_id):
    """Supprimer une actualité"""
    actualite = Actualite.query.get_or_404(actualite_id)
    
    if current_user.id != actualite.auteur_id and current_user.role != 'administrateur':
        abort(403)
    
    delete_associated_files(actualite)
    db.session.delete(actualite)
    db.session.commit()
    
    flash('Actualité supprimée avec succès!', 'success')
    return redirect(url_for('actualites.liste_actualites'))

# Route pour supprimer une pièce jointe (mentionnée dans le template)
@actualites_bp.route('/pieces-jointes/<int:piece_id>/supprimer')
@login_required
def supprimer_piece_jointe(piece_id):
    """Supprimer une pièce jointe"""
    piece = PieceJointe.query.get_or_404(piece_id)
    actualite = piece.actualite
    
    if current_user.id != actualite.auteur_id and current_user.role != 'administrateur':
        abort(403)
    
    # Supprimer le fichier physique
    try:
        relative_path = piece.url.replace('/static/', '')
        file_path = os.path.join(current_app.root_path, 'static', relative_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass
    
    db.session.delete(piece)
    db.session.commit()
    
    flash('Fichier supprimé avec succès!', 'success')
    return redirect(url_for('actualites.modifier_actualite', actualite_id=actualite.id))

# ========================
# ADMIN-ONLY ROUTES
# ========================

@actualites_bp.route('/admin/actualites')
@login_required
def admin_actualites():
    """Interface d'administration des actualités"""
    if current_user.role != 'administrateur':
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    statut = request.args.get('statut', '')
    q = request.args.get('q', '')
    categorie = request.args.get('categorie', '')
    
    query = Actualite.query.order_by(Actualite.date_publication.desc())
    
    # Filtres
    if statut and statut != 'tous':
        query = query.filter_by(statut=statut)
    
    if q:
        query = query.filter(Actualite.titre.contains(q))
    
    if categorie:
        query = query.filter_by(categorie=categorie)
    
    actualites = query.paginate(page=page, per_page=10, error_out=False)

    # Statistiques globales pour l'admin
    stats = {
        "total": Actualite.query.count(),
        "publie": Actualite.query.filter_by(statut="publie").count(),
        "brouillon": Actualite.query.filter_by(statut="brouillon").count(),
        "archive": Actualite.query.filter_by(statut="archive").count(),
        "commentaires": Commentaire.query.count(),
    }

    # Liste des catégories distinctes pour les filtres
    categories_result = db.session.query(Actualite.categorie).distinct().filter(Actualite.categorie.isnot(None)).all()
    categories = [cat[0] for cat in categories_result if cat[0]]

    return render_template(
        'actualites/actualites.html',
        actualites=actualites,
        statut=statut,
        stats=stats,
        categories=categories,
    )

@actualites_bp.route('/admin/actualites/<int:actualite_id>/toggle', methods=['POST'])
@login_required
def toggle_actualite(actualite_id):
    """Basculer le statut d'une actualité (admin seulement)"""
    if current_user.role != 'administrateur':
        abort(403)
    
    actualite = Actualite.query.get_or_404(actualite_id)
    actualite.statut = 'archive' if actualite.statut == 'publie' else 'publie'
    db.session.commit()
    
    flash(f'Actualité {"archivée" if actualite.statut == "archive" else "publiée"} avec succès!', 'success')
    return redirect(url_for('actualites.admin_actualites'))

@actualites_bp.route('/admin/actualites/<int:actualite_id>/supprimer', methods=['POST'])
@login_required
def admin_supprimer_actualite(actualite_id):
    """Supprimer une actualité (admin seulement)"""
    if current_user.role != 'administrateur':
        abort(403)
    
    actualite = Actualite.query.get_or_404(actualite_id)
    delete_associated_files(actualite)
    db.session.delete(actualite)
    db.session.commit()
    
    flash('Actualité supprimée avec succès!', 'success')
    return redirect(url_for('actualites.admin_actualites'))