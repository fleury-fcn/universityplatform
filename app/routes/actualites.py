from flask import Blueprint, render_template



actualitesebp = Blueprint('actualites', __name__)

@actualitesebp.route('/actualite/<int:id>')
def actualite_detail(id):
    # Ici vous récupéreriez normalement l'actualité depuis la base de données
    # Pour l'exemple, nous utilisons des données statiques
    actualite = {
        'id': id,
        'titre': "Journée Portes Ouvertes 2024",
        'categorie': "Événement",
        'date': "15 Novembre 2024",
        'auteur': "Direction de la Communication",
        'image': "https://source.unsplash.com/random/1200x600/?university,event",
        'contenu': """..."""  # Le contenu complet de l'actualité
    }
    
    return render_template('actualite_detail.html', actualite=actualite)