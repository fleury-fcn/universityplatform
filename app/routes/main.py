from flask import Blueprint, render_template
from app.models.actualites import Actualite

mainbp = Blueprint('main', __name__)

# Ma Page d'Accueil
@mainbp.route('/', methods = ['GET'])
def Page_Accueil():
        actualites_recentes = Actualite.query.order_by(Actualite.date_publication.desc()).limit(5).all()
        return render_template('HomePage.html', actualites_recentes=actualites_recentes)
