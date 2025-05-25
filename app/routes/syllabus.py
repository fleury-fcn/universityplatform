
from flask import Blueprint, render_template
from ..models.addsyllabus import Course  # Assurez-vous que le chemin est correct
from app.extensions import db  # Importez votre instance de base de données

syllabusbp = Blueprint('syllabusbp', __name__)

@syllabusbp.route('/syllabus', methods=['GET'])
def syllabus():
    # Récupérer tous les syllabus depuis la table addsyllabus
    syllabus_list = Course.query.all()  # Utilisez le modèle Course pour récupérer les données
    return render_template('syllabus.html', syllabi=syllabus_list)

