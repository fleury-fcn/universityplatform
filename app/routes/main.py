from flask import Blueprint, render_template

mainbp = Blueprint('main', __name__)

# Ma Page d'Accueil
@mainbp.route('/', methods = ['GET'])
def Page_Accueil():
        return render_template('HomePage.html')
