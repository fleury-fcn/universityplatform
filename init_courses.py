import logging
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models.courses import Cours, Professeur
from app.models.Users import User

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_courses():
    app = create_app()
    
    with app.app_context():
        try:
            # Vérification de l'existence d'un administrateur
            admin = User.query.filter_by(role='administrateur').first()
            if not admin:
                logger.error("Aucun administrateur trouvé dans la base de données")
                return

            # Création des professeurs s'ils n'existent pas
            professeurs_data = [
                {
                    'nom': 'KARIMUMURYANGO',
                    'prenom': 'Menedore',
                    'avatar': 'prof1.jpg'
                },
                {
                    'nom': 'NIYONSABA',
                    'prenom': 'Therence',
                    'avatar': 'prof2.jpg'
                },
                {
                    'nom': 'MVUYEKURE ',
                    'prenom': 'Mathieu',
                    'avatar': 'prof3.jpg'
                }
            ]

            professeurs = {}
            for data in professeurs_data:
                prof = Professeur.query.filter_by(nom=data['nom'], prenom=data['prenom']).first()
                if not prof:
                    prof = Professeur(**data)
                    db.session.add(prof)
                    logger.info(f"Professeur ajouté : {data['prenom']} {data['nom']}")
                else:
                    logger.info(f"Professeur existant : {data['prenom']} {data['nom']}")
                professeurs[f"{data['prenom']} {data['nom']}"] = prof.id

            db.session.commit()

            # Données des cours à initialiser
            courses_data = [
                {
                    'code': 'ACTU101',
                    'titre': 'Introduction à l\'Actuariat',
                    'description': 'Principes de base de l\'actuariat et calcul des primes.',
                    'credits': 4,
                    'cycle': 'bac',
                    'annee': 1,
                    'departement': 'actuariat',
                    'parcours': None,
                    'semestre': 1,
                    'specialisation': 'all',
                    'horaire': 'Lundi 10h-12h',
                    'lieu': 'Amphi A1',
                    'fichier': 'actuariat_intro.pdf',
                    'professeur_id': professeurs['KARIMUMURYANGO Menedore'],
                    'date_ajout': datetime.utcnow()
                },
                {
                    'code': 'DATA501',
                    'titre': 'Machine Learning Avancé',
                    'description': 'Algorithmes avancés d\'apprentissage automatique et leurs applications.',
                    'credits': 5,
                    'cycle': 'bac',
                    'annee': 1,
                    'departement': 'genie',
                    'parcours': None,
                    'semestre': 1,
                    'specialisation': 'data',
                    'horaire': 'Mardi 9h-12h',
                    'lieu': 'Labo IA',
                    'fichier': 'ml_avance.pdf',
                    'professeur_id': professeurs['NIYONSABA Therence'],
                    'date_ajout': datetime.utcnow()
                },
                {
                    'code': 'PROBA301',
                    'titre': 'Processus Stochastiques',
                    'description': 'Introduction aux processus stochastiques avec applications en modélisation.',
                    'credits': 4,
                    'cycle': 'bac',
                    'annee': 3,
                    'departement': 'probastate',
                    'parcours': None,
                    'semestre': 2,
                    'specialisation': 'all',
                    'horaire': 'Jeudi 13h-15h',
                    'lieu': 'Salle B4',
                    'fichier': 'processus_stochastiques.pdf',
                    'professeur_id': professeurs['MVUYEKURE Mathieu'],
                    'date_ajout': datetime.utcnow()
                },
                {
                    'code': 'SAID401',
                    'titre': 'Génie Logiciel Avancé',
                    'description': 'Introduction au Génie Logiciel Avancé pour le développement des applications.',
                    'credits': 4,
                    'cycle': 'master',
                    'annee': 4,
                    'departement': None,
                    'parcours': 'said',
                    'semestre': 1,
                    'specialisation': 'all',
                    'horaire': 'Jeudi 13h-15h',
                    'lieu': 'Salle Virtuelle ISTA',
                    'fichier': 'genie_logiciel.pdf',
                    'professeur_id': professeurs['MVUYEKURE Mathieu'],
                    'date_ajout': datetime.utcnow()
                }
            ]

            for data in courses_data:
                # Vérifie si le cours existe déjà
                if not Cours.query.filter_by(code=data['code']).first():
                    cours = Cours(**data)
                    db.session.add(cours)
                    logger.info(f"Cours ajouté : {data['code']} - {data['titre']}")
                else:
                    logger.info(f"Cours déjà existant : {data['code']} - {data['titre']}")

            db.session.commit()
            logger.info(f"{len(courses_data)} cours initialisés avec succès")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de l'initialisation des cours : {str(e)}", exc_info=True)
        finally:
            db.session.close()

if __name__ == '__main__':
    init_courses()