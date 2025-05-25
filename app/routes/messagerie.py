from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, jsonify, send_from_directory
from flask_login import login_required, current_user
from ..models.messagerie import Message, message_recipients
from ..models.Users import User
from app.extensions import db
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import json

messagerie_bp = Blueprint('messagerie', __name__)

# Configuration pour les uploads (sans current_app)
UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'messages')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_folder():
    """Helper function to get upload folder with app context"""
    return os.path.join(current_app.root_path, 'static', 'uploads', 'messages')

@messagerie_bp.route('/messagerie')
@login_required
def PageMessagerie():
    try:
        active_tab = request.args.get('tab', 'received')
        
        # Messages reçus
        received_messages = db.session.query(Message).join(
            message_recipients,
            (Message.id == message_recipients.c.message_id)
        ).filter(
            message_recipients.c.user_id == current_user.id,
            message_recipients.c.is_deleted == False
        ).order_by(Message.sent_at.desc()).all()
        
        # Messages envoyés
        sent_messages = Message.query.filter(
            Message.sender_id == current_user.id
        ).order_by(Message.sent_at.desc()).all()
        
        return render_template('messagerie/PageMessagerie.html',
                            received_messages=received_messages,
                            sent_messages=sent_messages,
                            active_tab=active_tab,
                            current_date=datetime.now().strftime("%d/%m/%Y"))
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        flash("Une erreur est survenue lors du chargement des messages", "error")
        return redirect(url_for('principale.Page_Principale'))

@messagerie_bp.route('/messagerie/envoyer', methods=['GET', 'POST'])
@login_required
def envoyer_message():
    if request.method == 'POST':
        recipients_emails = request.form.getlist('recipients')
        subject = request.form.get('subject', '').strip()
        content = request.form.get('content').strip()
        
        # Validation
        if not recipients_emails:
            flash('Veuillez spécifier au moins un destinataire', 'error')
            return redirect(url_for('messagerie.envoyer_message'))
        
        if not content:
            flash('Le message ne peut pas être vide', 'error')
            return redirect(url_for('messagerie.envoyer_message'))

        try:
            # Get upload folder with app context
            upload_folder = get_upload_folder()
            os.makedirs(upload_folder, exist_ok=True)
            
            # Traitement des pièces jointes
            attachments = []
            # Dans la route envoyer_message
            if 'attachments' in request.files:
                for file in request.files.getlist('attachments'):
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'messages')
                        os.makedirs(upload_folder, exist_ok=True)
                        filepath = os.path.join(upload_folder, filename)
            
                        # Enregistrer le fichier
                        file.save(filepath)
            
                        # Stocker uniquement le nom du fichier, pas le chemin complet
                        attachments.append({
                            'name': filename,
                            'size': os.path.getsize(filepath)
                        })

            # Création du message
            message = Message(
                sender_id=current_user.id,
                subject=subject if subject else "(sans objet)",
                content=content,
                attachments=attachments
            )

            # Ajout des destinataires
            valid_recipients = False
            for email in recipients_emails:
                recipient = User.query.filter_by(email=email).first()
                if recipient and recipient.id != current_user.id:
                    message.recipients.append(recipient)
                    valid_recipients = True

            if not valid_recipients:
                flash('Aucun destinataire valide spécifié', 'error')
                return redirect(url_for('messagerie.envoyer_message'))

            db.session.add(message)
            db.session.commit()
            flash('Message envoyé avec succès', 'success')
            return redirect(url_for('messagerie.PageMessagerie'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur envoi message: {str(e)}")
            flash(f"Une erreur est survenue lors de l'envoi du message: {str(e)}", "error")
            
    # GET - Afficher le formulaire avec les destinataires présélectionnés
    destinataires = request.args.getlist('destinataires')
    all_users = User.query.filter(User.id != current_user.id).all()
    
    return render_template('messagerie/envoyer_message.html',
                         all_users=all_users,
                         destinataires_pre=destinataires,
                         current_date=datetime.now().strftime("%d/%m/%Y"))

# Dans routes/messagerie.py
@messagerie_bp.route('/messagerie/corbeille')
@login_required
def corbeille():
    try:
        # Messages supprimés par l'utilisateur
        # En tant qu'expéditeur
        sent_deleted = Message.query.filter(
            Message.sender_id == current_user.id,
            Message.is_deleted_by_sender == True
        ).all()
        
        # En tant que destinataire
        received_deleted = db.session.query(Message).join(
            message_recipients,
            (Message.id == message_recipients.c.message_id) &
            (message_recipients.c.user_id == current_user.id) &
            (message_recipients.c.is_deleted == True)
        ).all()
        
        deleted_messages = sent_deleted + received_deleted
        
        return render_template('messagerie/corbeille.html', 
                            messages=deleted_messages,
                            current_date=datetime.now().strftime("%d/%m/%Y"))
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        flash("Une erreur est survenue lors du chargement de la corbeille", "error")
        return redirect(url_for('messagerie.PageMessagerie'))

@messagerie_bp.route('/messagerie/supprimer/<int:message_id>', methods=['POST'])
@login_required
def supprimer_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    try:
        message.mark_as_deleted(current_user.id)
        flash('Message déplacé dans la corbeille', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"ERREUR: {str(e)}")
        flash("Une erreur est survenue lors de la suppression", "error")
    
    return redirect(request.referrer or url_for('messagerie.PageMessagerie'))

@messagerie_bp.route('/messagerie/restaurer/<int:message_id>', methods=['POST'])
@login_required
def restaurer_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    try:
        message.mark_as_restored(current_user.id)
        flash('Message restauré avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"ERREUR: {str(e)}")
        flash("Une erreur est survenue lors de la restauration", "error")
    
    return redirect(url_for('messagerie.corbeille'))

@messagerie_bp.route('/messagerie/supprimer-definitivement/<int:message_id>', methods=['POST'])
@login_required
def supprimer_definitivement(message_id):
    message = Message.query.get_or_404(message_id)
    
    try:
        # Vérifier que l'utilisateur a bien supprimé le message
        if not message.is_deleted_by(current_user.id):
            flash('Action non autorisée', 'error')
            return redirect(url_for('messagerie.corbeille'))
            
        # Supprimer les pièces jointes
        if message.attachments:
            for attachment in message.attachments:
                try:
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], attachment['name'])
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except Exception as e:
                    print(f"Erreur suppression fichier {attachment['name']}: {str(e)}")
        
        db.session.delete(message)
        db.session.commit()
        flash('Message supprimé définitivement', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"ERREUR: {str(e)}")
        flash("Une erreur est survenue lors de la suppression", "error")
    
    return redirect(url_for('messagerie.corbeille'))

@messagerie_bp.route('/download_attachment/<int:message_id>/<path:attachment_name>')
@login_required
def download_attachment(message_id, attachment_name):
    message = Message.query.get_or_404(message_id)
    
    # Verify user has access to this message
    if message.sender_id != current_user.id and current_user.id not in [r.id for r in message.recipients]:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('messagerie.PageMessagerie'))

    # Find the specific attachment
    attachment = next((a for a in message.attachments if a['name'] == attachment_name), None)
    if not attachment:
        flash('Pièce jointe introuvable', 'error')
        return redirect(url_for('messagerie.voir_message', message_id=message_id))

    # Secure file path
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'messages')
    filepath = os.path.join(upload_folder, secure_filename(attachment_name))
    
    if not os.path.exists(filepath):
        flash('Fichier introuvable sur le serveur', 'error')
        return redirect(url_for('messagerie.voir_message', message_id=message_id))
    
    return send_from_directory(
        directory=upload_folder,
        path=secure_filename(attachment_name),
        as_attachment=True
    )

@messagerie_bp.route('/messagerie/<int:message_id>')
@login_required
def voir_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    # Vérification des droits
    if message.sender_id != current_user.id and current_user.id not in [r.id for r in message.recipients]:
        flash('Accès non autorisé', 'error')
        return redirect(url_for('messagerie.PageMessagerie'))
    
    # Marquer comme lu si c'est un destinataire
    if current_user.id in [r.id for r in message.recipients] and not message.is_read_by(current_user.id):
        try:
            db.session.execute(
                message_recipients.update()
                .where(message_recipients.c.message_id == message_id)
                .where(message_recipients.c.user_id == current_user.id)
                .values(read_at=datetime.utcnow())
            )
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"ERREUR marquage comme lu: {str(e)}")
    
    return render_template('messagerie/voir_message.html', 
                         message=message,
                         current_date=datetime.now().strftime("%d/%m/%Y"))

@messagerie_bp.route('/get_presence_updates')
@login_required
def get_presence_updates():
    try:
        # Retourne la liste des utilisateurs avec leur statut
        users = User.query.filter(User.id != current_user.id).all()
        return jsonify([{
            'email': user.email,
            'status': user.get_presence_status(),  # À implémenter dans votre modèle User
            'name': user.nom_complet,
            'avatar': user.get_avatar_url()
        } for user in users])
    except Exception as e:
        print(f"ERREUR get_presence_updates: {str(e)}")
        return jsonify([])



@messagerie_bp.route('/messagerie/marquer-comme-lu/<int:message_id>', methods=['POST'])
@login_required
def marquer_comme_lu(message_id):
    try:
        # Mettre à jour directement dans la table de liaison
        db.session.execute(
            message_recipients.update()
            .where(message_recipients.c.message_id == message_id)
            .where(message_recipients.c.user_id == current_user.id)
            .values(read_at=datetime.utcnow())
        )
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    

def clean_orphan_attachments():
    """Supprime les fichiers sans message associé"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'messages')
    
    # Tous les fichiers physiques
    physical_files = set(os.listdir(upload_folder))
    
    # Tous les fichiers référencés
    referenced_files = set()
    for message in Message.query.all():
        for att in message.attachments:
            referenced_files.add(att['name'])
    
    # Fichiers orphelins
    orphan_files = physical_files - referenced_files
    
    # Suppression
    for filename in orphan_files:
        try:
            os.remove(os.path.join(upload_folder, filename))
            print(f"Supprimé: {filename}")
        except Exception as e:
            print(f"Erreur suppression {filename}: {str(e)}")


@messagerie_bp.route('/selection_destinataires', methods=['GET', 'POST'])
@login_required
def selection_destinataires():
    if request.method == 'POST':
        selected_emails = request.form.getlist('destinataires')
        if not selected_emails:
            flash('Veuillez sélectionner au moins un destinataire.', 'error')
            return redirect(url_for('messagerie.selection_destinataires'))
        return redirect(url_for('messagerie.envoyer_message', destinataires=selected_emails))
    
    all_users = User.query.filter(User.id != current_user.id).all()
    print(f"Nombre d'utilisateurs: {len(all_users)}")  # Debug
    return render_template('messagerie/selection_destinataires.html',
                           all_users=all_users,
                           current_date=datetime.now().strftime("%d/%m/%Y"))