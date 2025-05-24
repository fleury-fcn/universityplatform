
from flask import Blueprint

# Créer un Blueprint pour les routes des résultats
bp = Blueprint('results', __name__)

@bp.route('/results', methods=['GET'])
def get_results():
    return "Liste des résultats"