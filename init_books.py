import logging
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models.books import Book
from app.models.Users import User

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_books():
    app = create_app()
    
    with app.app_context():
        try:
            # Vérification de l'existence d'un administrateur
            admin = User.query.filter_by(role='administrateur').first()
            if not admin:
                logger.error("Aucun administrateur trouvé dans la base de données")
                return

            # Données des livres à initialiser
            books_data = [
                {
                    'title': 'Statistique Descriptive Appliquée',
                    'author': 'Jean Dupont',
                    'description': 'Manuel complet de statistique descriptive avec exercices corrigés',
                    'category': 'statistique',
                    'language': 'fr',
                    'level': 'bac',
                    'file_path': 'statistique_descriptive.pdf',
                    'file_size': 5200,
                    'file_type': 'pdf',
                    'user_id': admin.id,
                    'upload_date': datetime.utcnow()
                },
                {
                    'title': 'Théorie des Probabilités',
                    'author': 'Marie Lambert',
                    'description': 'Fondements théoriques des probabilités et applications',
                    'category': 'probabilite',
                    'language': 'fr',
                    'level': 'master',
                    'file_path': 'theorie_probabilites.pdf',
                    'file_size': 7800,
                    'file_type': 'pdf',
                    'user_id': admin.id,
                    'upload_date': datetime.utcnow()
                },
                {
                    'title': 'Actuarial Mathematics',
                    'author': 'Robert Brown',
                    'description': 'Comprehensive guide to actuarial mathematics for insurance',
                    'category': 'actuariat',
                    'language': 'en',
                    'level': 'master',
                    'file_path': 'actuarial_math.pdf',
                    'file_size': 9100,
                    'file_type': 'pdf',
                    'user_id': admin.id,
                    'upload_date': datetime.utcnow()
                },
                {
                    'title': 'Data Science with Python',
                    'author': 'Ahmed Benali',
                    'description': 'Practical introduction to data science using Python',
                    'category': 'data-science',
                    'language': 'en',
                    'level': 'master',
                    'file_path': 'data_science_python.pdf',
                    'file_size': 6500,
                    'file_type': 'pdf',
                    'user_id': admin.id,
                    'upload_date': datetime.utcnow()
                },
                {
                    'title': 'Algorithmique et Programmation',
                    'author': 'Sophie Martin',
                    'description': 'Fondamentaux de l\'algorithmique et programmation en Python',
                    'category': 'informatique',
                    'language': 'fr',
                    'level': 'bac',
                    'file_path': 'algorithmique_programmation.pdf',
                    'file_size': 4700,
                    'file_type': 'pdf',
                    'user_id': admin.id,
                    'upload_date': datetime.utcnow()
                },
                {
                    'title': 'Méthodologie de Recherche',
                    'author': 'Institut Statistique',
                    'description': 'Guide pratique pour la rédaction de mémoires et thèses',
                    'category': 'divers',
                    'language': 'fr',
                    'level': 'all',
                    'file_path': 'methodologie_recherche.pdf',
                    'file_size': 3900,
                    'file_type': 'pdf',
                    'user_id': admin.id,
                    'upload_date': datetime.utcnow()
                }
            ]

            for data in books_data:
                # Vérifie si le livre existe déjà
                if not Book.query.filter_by(title=data['title'], author=data['author']).first():
                    book = Book(**data)
                    db.session.add(book)
                    logger.info(f"Livre ajouté : {data['title']} - {data['author']}")
                else:
                    logger.info(f"Livre déjà existant : {data['title']} - {data['author']}")

            db.session.commit()
            logger.info(f"{len(books_data)} livres initialisés avec succès")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de l'initialisation des livres : {str(e)}", exc_info=True)
        finally:
            db.session.close()

if __name__ == '__main__':
    init_books()