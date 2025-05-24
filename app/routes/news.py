
from flask import Blueprint

# Créer un Blueprint pour les routes des actualités
bp = Blueprint('news', __name__)

@bp.route('/news', methods=['GET'])
def get_news():
    return "Liste des actualités"