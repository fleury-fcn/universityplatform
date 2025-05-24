
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime

principalebp = Blueprint('principale', __name__)

# Ma page d'Accueil
@principalebp.route('/PagePrincipale', methods=['GET', 'POST'])
@login_required  # Protection de la route - utilisateur doit être connecté
def Page_Principale():
    # Formatage de la date en français (ex: "25 avril 2024")
    current_date = datetime.now().strftime("%d %B %Y")
    
    return render_template(
        'PagePrincipale.html',
        current_user=current_user,  # Passe automatiquement l'utilisateur connecté
        current_date=current_date  # Passe la date formatée
    )