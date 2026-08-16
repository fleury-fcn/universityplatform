import logging
from datetime import datetime, UTC  # Modifié pour utiliser UTC
from app import create_app
from app.extensions import db
from app.models.tuyaux import Tuyau
from app.models.Users import User

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_tuyaux():
    app = create_app()
    
    with app.app_context():
        try:
            # Récupération de tous les utilisateurs
            users = User.query.all()
            
            # Vérification qu'il y a au moins un utilisateur
            if not users:
                logger.error("Aucun utilisateur trouvé dans la base de données")
                return

            # Données des tuyaux à initialiser
            tuyaux_data = [
                {
                    'titre': 'Examens corrigés - Actuariat 1ère année',
                    'description': 'Collection d\'examens corrigés en actuariat pour la 1ère année avec solutions détaillées.',
                    'matiere': 'Mathématiques Financières',
                    'cycle': 'bac',
                    'niveau': 1,
                        'departement': 'ACTU',
                    'semestre': 1,
                    'annee_academique': '2022-2023',
                    'type_fichier': 'pdf',
                    'fichier': 'exam_actuariat1_2023.pdf',
                    'utilisateur_id': users[0].id,  # Premier utilisateur
                    'date_ajout': datetime.now(UTC)  # Modifié pour utiliser UTC
                },
                {
                    'titre': 'Astuces pour l\'examen de Statistique',
                    'description': 'Conseils et méthodes pour réussir l\'examen de statistique descriptive.',
                    'matiere': 'Statistique Descriptive',
                    'cycle': 'bac',
                    'niveau': 2,
                        'departement': 'GENSTAT',
                    'semestre': 2,
                    'annee_academique': '2021-2022',
                    'type_fichier': 'docx',
                    'fichier': 'astuces_stat.docx',
                    'utilisateur_id': users[0].id,  # Même utilisateur
                    'date_ajout': datetime.now(UTC)  # Modifié pour utiliser UTC
                }
            ]

            # Si vous avez au moins 3 utilisateurs, ajoutez d'autres tuyaux
            if len(users) >= 3:
                tuyaux_data.extend([
                    {
                        'titre': 'Annales Machine Learning Master',
                        'description': 'Sujets d\'examens des 3 dernières années en Machine Learning avec corrigés types.',
                        'matiere': 'Machine Learning',
                        'cycle': 'master',
                        'niveau': 4,
                            'departement': 'GENSTAT',
                        'semestre': 1,
                        'annee_academique': '2023-2024',
                        'type_fichier': 'pdf',
                        'fichier': 'annales_ml_master.pdf',
                        'utilisateur_id': users[1].id,
                        'date_ajout': datetime.now(UTC)
                    },
                    {
                        'titre': 'Guide de révision Probabilités',
                        'description': 'Fiche de révision complète pour l\'examen de probabilités avec exemples pratiques.',
                        'matiere': 'Probabilités',
                        'cycle': 'bac',
                        'niveau': 3,
                            'departement': 'PROBA',
                        'semestre': 2,
                        'annee_academique': '2020-2021',
                        'type_fichier': 'pptx',
                        'fichier': 'revision_proba.pptx',
                        'utilisateur_id': users[2].id,
                        'date_ajout': datetime.now(UTC)
                    }
                ])

            for data in tuyaux_data:
                if not Tuyau.query.filter_by(titre=data['titre'], utilisateur_id=data['utilisateur_id']).first():
                    tuyau = Tuyau(**data)
                    db.session.add(tuyau)
                    logger.info(f"Tuyau ajouté : {data['titre']} par l'utilisateur {data['utilisateur_id']}")
                else:
                    logger.info(f"Tuyau déjà existant : {data['titre']}")

            db.session.commit()
            logger.info(f"{len(tuyaux_data)} tuyaux initialisés avec succès")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de l'initialisation des tuyaux : {str(e)}", exc_info=True)
        finally:
            db.session.close()

if __name__ == '__main__':
    init_tuyaux()