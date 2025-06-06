from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime
from app.models.actualites import Actualite

principalebp = Blueprint('principale', __name__)

@principalebp.route('/PagePrincipale', methods=['GET', 'POST'])
@login_required
def Page_Principale():
    # Formatage de la date en français (ex: "25 avril 2024")
    current_date = datetime.now().strftime("%d %B %Y")
    actualites_recentes = Actualite.query.filter_by(statut='publie').order_by(Actualite.date_publication.desc()).limit(6).all()
    return render_template(
        'PagePrincipale.html',
        current_user=current_user,
        current_date=current_date,
        actualites_recentes=actualites_recentes
    )