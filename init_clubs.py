import logging
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models.clubs import Club
from app.models.Users import User  
from werkzeug.security import generate_password_hash, check_password_hash

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_clubs():
    app = create_app()
    
    with app.app_context():
        try:
            # Vérifiez qu'il y a au moins un admin dans la base
            admin = User.query.filter_by(role='administrateur').first()
            '''if not admin:
                admin = User(
                username='admin_temp',
                email='admin@temp.com',
                role='admin',
                password_hash=generate_password_hash('temp_password'),
                prenom='Admin', 
                nom='System'
            )'''

            db.session.add(admin)
            db.session.commit()
            logger.warning("Admin temporaire créé pour l'initialisation")

            clubs_data = [
                {
                    'title': 'Informatique Decisionnelle Club',
                    'description': 'Le club Informatique Decisionnelle de l\'ISTA où nous explorons les dernières innovations du monde Informatique, organisons des Sciences de formation pour preparer les Génies de l\'Informatique et Statistique de demain.',
                    'category': 'technologie',
                    'banner': 'tech-banner.jpg',
                    'logo': 'tech-logo.jpg',
                    'meeting_frequency': 'Réunion hebdomadaire',
                    'tags': 'Intelligence Artificielle,Programmation en Python,Developpement des Applications Web et Mobile',
                    'admin_id': admin.id,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'Actuariat Club',
                    'description': 'Le voyage dans le monde de l\'Assurance et de la finance se passe ici, il est ouvert à tout le monde qui desire avoir une tete bien faite et bien pleine en Sciences Actuarielles',
                    'category': 'science',
                    'banner': 'sport-banner.jpg',
                    'logo': 'sport-logo.jpg',
                    'meeting_frequency': '3x/semaine',
                    'tags': 'Tarification en Assurance IARD,Gestion des risques Financiers',
                    'admin_id': admin.id,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'Club d\'Actualité Economique',
                    'description': 'Pour les passionnés de l\'actuaritité Economique, cet espace est le votre.',
                    'category': 'social',
                    'banner': 'data-banner.jpg',
                    'logo': 'data-logo.jpg',
                    'meeting_frequency': '2x/mois',
                    'tags': 'Taux d\'inflation,Crise Economique,Banques des jeunes',
                    'admin_id': admin.id,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'Genie en Herbes',
                    'description': 'Pour devenir un intellectuel bien informé, cultivé, voici l\'endroit qui te convient.',
                    'category': 'art',
                    'banner': 'eco-banner.jpg',
                    'logo': 'eco-logo.jpg',
                    'meeting_frequency': '1x/semaine',
                    'tags': 'Rubriques Question Reponse,Histoire',
                    'admin_id': admin.id,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'English Club ISTA',
                    'description': 'You dream to increase your English Level and become fluent like a native speaker.We are here for You.',
                    'category': 'social',
                    'banner': 'art-banner.jpg',
                    'logo': 'art-logo.jpg',
                    'meeting_frequency': 'Variable',
                    'tags': 'English for Biginner,English advenced Level',
                    'admin_id': admin.id,
                    'created_at': datetime.utcnow()
                },
                {
                    'title': 'ISTA Entrepreneurs',
                    'description': 'Pour les futurs entrepreneurs. Ateliers de création d\'entreprise, rencontres avec des startups et préparation au monde professionnel.',
                    'category': 'entrepreneuriat',
                    'banner': 'entrepreneur-banner.jpg',
                    'logo': 'entrepreneur-logo.jpg',
                    'meeting_frequency': '1x/semaine',
                    'tags': 'Entrepreneuriat,Startup,Business',
                    'admin_id': admin.id,
                    'created_at': datetime.utcnow()
                }
            ]


            for data in clubs_data:
                # Vérifie si le club existe déjà
                if not Club.query.filter_by(title=data['title']).first():
                    club = Club(**data)
                    db.session.add(club)
                    logger.info(f"Club ajouté : {data['title']}")
                else:
                    logger.info(f"Club déjà existant : {data['title']}")

            db.session.commit()
            logger.info(f"{len(clubs_data)} clubs initialisés avec succès")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de l'initialisation : {str(e)}", exc_info=True)
        finally:
            db.session.close()

if __name__ == '__main__':
    init_clubs()