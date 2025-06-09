from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models.addsyllabus import Course
from app.extensions import db
from werkzeug.utils import secure_filename
import os
import requests

addsyllabusbp = Blueprint('addsyllabus', __name__)

# Taille maximale du fichier (en octets)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 Mo

@addsyllabusbp.route('/addsyllabus', methods=['GET', 'POST'])
@login_required
def addsyllabus():
    if request.method == 'POST':
        title = request.form['title']
        code = request.form['code']
        department = request.form['department']
        level = request.form['level']
        credits = 0  # Ajustez si nécessaire
        description = request.form.get('description', '')
        cycle = 'bac'  # Ajustez si nécessaire

        file = request.files.get('file')
        file_path = None
        file_size = None

        if file and file.filename:
            # Vérification de la taille du fichier uploadé
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)
            if size > MAX_FILE_SIZE:
                flash('Le fichier est trop volumineux. Taille maximale : 5 Mo.', 'danger')
                return redirect(url_for('addsyllabusbp.addsyllabus'))

            upload_folder = 'app/static/uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            file_size = size
        else:
            url = request.form.get('url')
            if url:
                try:
                    response = requests.get(url)
                    response.raise_for_status()  # Vérifie si la requête a réussi

                    # Vérifie la taille du fichier téléchargé
                    if len(response.content) > MAX_FILE_SIZE:
                        flash('Le fichier est trop volumineux. Taille maximale : 5 Mo.', 'danger')
                        return redirect(url_for('addsyllabusbp.addsyllabus'))

                    filename = secure_filename(url.split('/')[-1])  # Nommer le fichier à partir de l'URL
                    upload_folder = 'app/static/uploads'
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)

                    file_path = os.path.join(upload_folder, filename)
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    file_size = len(response.content)

                except requests.exceptions.RequestException as e:
                    flash(f'Erreur lors du téléchargement du fichier depuis l\'URL : {str(e)}', 'danger')
                    return redirect(url_for('addsyllabusbp.addsyllabus'))

        new_course = Course(
            title=title,
            code=code,
            department=department,
            year=int(level[-1]),  # Assurez-vous que 'level' est formaté correctement
            semester=1,  # Ajustez si nécessaire
            cycle=cycle,
            description=description,
            file_path=file_path,
            file_size=file_size,
            credits=credits
        )

        try:
            db.session.add(new_course)
            db.session.commit()
            flash('Syllabus ajouté avec succès!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout du syllabus : {str(e)}', 'danger')

        return redirect(url_for('addsyllabus.addsyllabus'))

    return render_template('Pageaddsyllabus.html', current_user=current_user)