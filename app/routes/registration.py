

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from sqlalchemy import desc
from ..extensions import db
from ..models.registration import InscriptionAcademique
from ..models.Documents import DocumentInscription
#from ..models.rechercheinscription import RechercheInscription
from flask_login import current_user, login_required

registrationbp = Blueprint('registrationbp', __name__)

# Configuration pour les fichiers uploadés
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
UPLOAD_FOLDER = 'static/uploads/documents'

def allowed_file(filename):
    """Vérifie si le fichier a une extension autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route pour l'enregistrement académique
@registrationbp.route('/inscription_academique', methods=['GET', 'POST'])
@login_required
def inscription():
    if current_user.role not in ['administrateur', 'etudiant']:
        abort(403, description="Accès réservé aux étudiants et administrateurs")

    inscription = InscriptionAcademique.query.filter_by(matricule=request.args.get('matricule')).first()

    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        matricule = request.form.get('matricule')
        genre = request.form.get('genre')
        date_naissance = request.form.get('date_naissance')
        email_institutionnel = request.form.get('email_institutionnel')
        annee_academique = request.form.get('annee_academique')
        niveau = request.form.get('niveau')
        departement = request.form.get('departement')
        specialisation = request.form.get('specialisation')

        # Vérification des champs obligatoires
        required_fields = [nom, prenom, matricule, genre, date_naissance, email_institutionnel, annee_academique, niveau, departement]
        if not all(required_fields):
            flash("Tous les champs obligatoires doivent être remplis", 'error')
            return redirect(url_for('registrationbp.inscription'))

        # Vérifier si le matricule existe déjà
        existing_inscription = InscriptionAcademique.query.filter_by(matricule=matricule).first()
        if existing_inscription:
            flash("Ce matricule existe déjà.", 'error')
            return redirect(url_for('registrationbp.inscription'))

        # Traitement de la date de naissance
        try:
            date_naissance = datetime.strptime(date_naissance, '%d/%m/%Y').date()
        except ValueError:
            flash("Format de date invalide (dd/mm/yyyy attendu)", 'error')
            return redirect(url_for('registrationbp.inscription'))

        try:
            if not inscription:
                inscription = create_new_inscription(date_naissance)
                action = "Création inscription"
            else:
                anciennes_valeurs = get_anciennes_valeurs(inscription)
                update_inscription(inscription, date_naissance)
                action = "Modification inscription"

            db.session.add(inscription)
            db.session.commit()
            flash('Informations enregistrées avec succès', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur base de données: {str(e)}", 'error')

        return redirect(url_for('registrationbp.inscription'))

    return render_inscription_template(inscription)

def create_new_inscription(date_naissance):
    """Crée une nouvelle inscription académique."""
    return InscriptionAcademique(
        nom=request.form['nom'],
        prenom=request.form['prenom'],
        matricule=request.form['matricule'],
        genre=request.form['genre'],
        date_naissance=date_naissance,
        email_institutionnel=request.form['email_institutionnel'],
        annee_academique=request.form['annee_academique'],
        niveau=request.form['niveau'],
        departement=request.form['departement'],
        specialisation=request.form.get('specialisation'),
        filiere=request.form.get('filiere')
    )

def get_anciennes_valeurs(inscription):
    """Récupère les anciennes valeurs avant modification."""
    return {
        'nom': inscription.nom,
        'prenom': inscription.prenom,
        'matricule': inscription.matricule,
        'genre': inscription.genre,
        'date_naissance': str(inscription.date_naissance),
        'annee_academique': inscription.annee_academique,
        'niveau': inscription.niveau,
        'departement': inscription.departement,
        'specialisation': inscription.specialisation
    }

def update_inscription(inscription, date_naissance):
    """Met à jour une inscription existante."""
    inscription.nom = request.form['nom']
    inscription.prenom = request.form['prenom']
    inscription.matricule = request.form['matricule']
    inscription.genre = request.form['genre']
    inscription.date_naissance = date_naissance
    inscription.email_institutionnel = request.form['email_institutionnel']
    inscription.annee_academique = request.form['annee_academique']
    inscription.niveau = request.form['niveau']
    inscription.departement = request.form['departement']
    inscription.specialisation = request.form.get('specialisation')

def handle_documents(inscription):
    """Gère l'upload des documents."""
    if not inscription:
        flash('Complétez d\'abord vos informations personnelles', 'warning')
        return redirect(url_for('registrationbp.inscription'))

    try:
        documents_ajoutes = []
        for doc_type in ['diplome', 'releve', 'photo', 'cin']:
            if doc_type not in request.files:
                continue

            file = request.files[doc_type]
            if file and allowed_file(file.filename):
                filename = process_uploaded_file(doc_type, file)
                doc = handle_document(inscription.id, doc_type, filename)
                documents_ajoutes.append(doc_type)

        db.session.commit()
        if documents_ajoutes:
            flash(f'Documents {", ".join(documents_ajoutes)} enregistrés', 'success')
        else:
            flash('Aucun nouveau document à enregistrer', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de l'enregistrement des documents: {str(e)}", 'error')

    return redirect(url_for('registrationbp.inscription'))

def process_uploaded_file(doc_type, file):
    """Traite le fichier uploadé et le sauvegarde."""
    filename = secure_filename(f"{doc_type}_{datetime.now().timestamp()}.{file.filename.rsplit('.', 1)[1].lower()}")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)
    return filename

def handle_document(inscription_id, doc_type, filename):
    """Gère l'enregistrement du document en base."""
    doc = DocumentInscription.query.filter_by(
        inscription_id=inscription_id,
        type_document=doc_type
    ).first()

    if doc:
        # Supprimer l'ancien fichier
        old_file = os.path.join(UPLOAD_FOLDER, doc.chemin_fichier)
        if os.path.exists(old_file):
            os.remove(old_file)

        doc.chemin_fichier = filename
        doc.est_valide = False
        doc.date_depot = datetime.utcnow()
    else:
        doc = DocumentInscription(
            inscription_id=inscription_id,
            type_document=doc_type,
            chemin_fichier=filename,
            date_depot=datetime.utcnow()
        )
        db.session.add(doc)

    return doc

def render_inscription_template(inscription):
    """Prépare et renvoie le template avec les données."""
    documents = {}

    if inscription:
        documents = {doc.type_document: doc for doc in inscription.documents}

    return render_template('PageInscriptionAcademique.html',
                           inscription=inscription,
                           documents=documents)

# API rechercher inscription
@registrationbp.route('/api/recherche/inscriptions', methods=['GET'])
@login_required
def rechercher_inscriptions():
    if current_user.role not in ['administrateur', 'etudiant']:
        abort(403, description="Accès réservé aux étudiants et administrateurs")

    matricule = request.args.get('matricule')
    nom = request.args.get('nom')
    prenom = request.args.get('prenom')
    niveau = request.args.get('niveau')

    query = InscriptionAcademique.query

    # Ajout des filtres uniquement si les paramètres sont fournis
    if matricule:
        query = query.filter(InscriptionAcademique.matricule.ilike(f'%{matricule}%'))
    if nom:
        query = query.filter(InscriptionAcademique.nom.ilike(f'%{nom}%'))
    if prenom:
        query = query.filter(InscriptionAcademique.prenom.ilike(f'%{prenom}%'))
    if niveau:
        query = query.filter(InscriptionAcademique.niveau == niveau)

    results = query.all()  # Récupère tous les résultats

    # Préparation des données pour la réponse
    data = [{
        'id': inscription.id,
        'matricule': inscription.matricule,
        'nom': inscription.nom,
        'prenom': inscription.prenom,
        'genre': inscription.genre,
        'date_naissance': inscription.date_naissance,
        'email_institutionnel': inscription.email_institutionnel,
        'annee_academique': inscription.annee_academique,
        'niveau': inscription.niveau,
        'departement': inscription.departement,
        'specialisation': inscription.specialisation,
        'filiere': inscription.filiere,
        'est_actif': inscription.est_actif,
        'est_confirme': inscription.est_confirme
    } for inscription in results]

    return jsonify({'data': data, 'total': len(data)})