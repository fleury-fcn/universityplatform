"""
Script d'initialisation des données de base
Départements, filières, et données de référence
"""
from app import create_app
from app.extensions import db
from app.models.enseignants import DepartementAcademique
from app.models.academique import Filiere, Classe, UniteEnseignement
from datetime import datetime

def init_base_data():
    """Initialise les données de base du système"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Initialisation des données de base...")
        
        try:
            annee_courante = f"{datetime.now().year}-{datetime.now().year + 1}"
            # Créer les départements académiques
            departements = [
                {
                    'code': 'ACTU',
                    'nom': 'Département Actuariat',
                    'description': 'Expertise en actuariat, assurance et gestion des risques'
                },
                {
                    'code': 'GENSTAT',
                    'nom': 'Département Génie Statistique',
                    'description': 'Statistique appliquée, sciences économiques et data science'
                },
                {
                    'code': 'PROBA',
                    'nom': 'Département Probabilités et Statistique',
                    'description': 'Modélisation probabiliste et recherche statistique avancée'
                }
            ]
            
            departements_map = {}
            for dept_data in departements:
                dept = DepartementAcademique.query.filter_by(code=dept_data['code']).first()
                if not dept:
                    dept = DepartementAcademique(**dept_data)
                    db.session.add(dept)
                    print(f"  ✓ Département créé: {dept_data['nom']}")
                else:
                    print(f"  - Département existant: {dept_data['nom']}")
                departements_map[dept_data['code']] = dept
            
            db.session.commit()
            
            # Créer les filières
            filieres = [
                # Bac +2 / Bac +3 Actuariat
                {
                    'code': 'ARISK',
                    'nom': 'Analyse des Risques',
                    'description': 'Filière Actuariat orientée assurance et risk management (bac+2)',
                    'cycle': 'licence',
                    'duree_annees': 3,
                    'departement_code': 'ACTU'
                },
                {
                    'code': 'APRED',
                    'nom': 'Analyses Prédictives',
                    'description': 'Filière Actuariat dédiée aux modèles prédictifs et actuariat vie (bac+2)',
                    'cycle': 'licence',
                    'duree_annees': 3,
                    'departement_code': 'ACTU'
                },
                # Bac +2 / Bac +3 Génie Statistique
                {
                    'code': 'SECO',
                    'nom': 'Sciences Économiques',
                    'description': 'Filière Génie Statistique axée sur l’analyse économique et la prospective',
                    'cycle': 'licence',
                    'duree_annees': 3,
                    'departement_code': 'GENSTAT'
                },
                {
                    'code': 'SDATA',
                    'nom': 'Sciences des Données',
                    'description': 'Filière Génie Statistique orientée data science et informatique décisionnelle',
                    'cycle': 'licence',
                    'duree_annees': 3,
                    'departement_code': 'GENSTAT'
                },
                # Bac +3 Probabilités & Statistique
                {
                    'code': 'PROBSTATS',
                    'nom': 'Probabilités et Statistique',
                    'description': 'Filière du département Probabilités et Statistique pour la recherche appliquée',
                    'cycle': 'licence',
                    'duree_annees': 3,
                    'departement_code': 'PROBA'
                },
                # Parcours Master
                {
                    'code': 'MACTU',
                    'nom': 'Master Actuariat et Finance',
                    'description': 'Parcours master spécialisé en actuariat avancé et finance quantitative',
                    'cycle': 'master',
                    'duree_annees': 2,
                    'departement_code': 'ACTU'
                },
                {
                    'code': 'MSAID',
                    'nom': 'Master Statistique Appliquée & Informatique Décisionnelle',
                    'description': 'Parcours master combinant modélisation statistique et systèmes décisionnels',
                    'cycle': 'master',
                    'duree_annees': 2,
                    'departement_code': 'GENSTAT'
                },
                {
                    'code': 'MMSP',
                    'nom': 'Master Modélisation Statistique et Probabilité',
                    'description': 'Parcours master orienté recherche en probabilités et statistiques avancées',
                    'cycle': 'master',
                    'duree_annees': 2,
                    'departement_code': 'PROBA'
                }
            ]
            
            filieres_map = {}
            for fil_data in filieres:
                data = fil_data.copy()
                dept_code = data.pop('departement_code', None)
                filiere = Filiere.query.filter_by(code=data['code']).first()
                if not filiere:
                    if dept_code:
                        dept = departements_map.get(dept_code) or DepartementAcademique.query.filter_by(code=dept_code).first()
                        data['departement_id'] = dept.id if dept else None
                    filiere = Filiere(**data)
                    db.session.add(filiere)
                    print(f"  ✓ Filière créée: {data['nom']}")
                else:
                    print(f"  - Filière existante: {data['nom']}")
                filieres_map[data['code']] = filiere
            
            db.session.commit()
            
            # Créer quelques classes de référence
            classes = [
                {'code': 'BAC2-ARISK-A', 'nom': 'BAC+2 Analyse des Risques', 'niveau': 'L2', 'filiere_code': 'ARISK'},
                {'code': 'BAC3-APRED-A', 'nom': 'BAC+3 Analyses Prédictives', 'niveau': 'L3', 'filiere_code': 'APRED'},
                {'code': 'BAC2-SECO-A', 'nom': 'BAC+2 Sciences Économiques', 'niveau': 'L2', 'filiere_code': 'SECO'},
                {'code': 'BAC3-SDATA-A', 'nom': 'BAC+3 Sciences des Données', 'niveau': 'L3', 'filiere_code': 'SDATA'},
                {'code': 'BAC3-PROBA-A', 'nom': 'BAC+3 Probabilités et Statistique', 'niveau': 'L3', 'filiere_code': 'PROBSTATS'},
                {'code': 'M1-ACTUFIN', 'nom': 'Master 1 Actuariat et Finance', 'niveau': 'M1', 'filiere_code': 'MACTU'},
                {'code': 'M1-SAID', 'nom': 'Master 1 Statistique Appliquée & ID', 'niveau': 'M1', 'filiere_code': 'MSAID'},
                {'code': 'M1-MSP', 'nom': 'Master 1 Modélisation Statistique', 'niveau': 'M1', 'filiere_code': 'MMSP'}
            ]
            for cls_data in classes:
                if not Classe.query.filter_by(code=cls_data['code']).first():
                    filiere = filieres_map.get(cls_data['filiere_code']) or Filiere.query.filter_by(code=cls_data['filiere_code']).first()
                    classe = Classe(
                        code=cls_data['code'],
                        nom=cls_data['nom'],
                        niveau=cls_data['niveau'],
                        filiere_id=filiere.id if filiere else None,
                        annee_academique=annee_courante,
                        effectif_max=45,
                        effectif_actuel=0,
                        est_active=True
                    )
                    db.session.add(classe)
                    print(f"  ✓ Classe créée: {cls_data['nom']}")
                else:
                    print(f"  - Classe existante: {cls_data['nom']}")
            db.session.commit()

            # Créer des UE de base
            ues = [
                {
                    'code': 'ARISK201',
                    'intitule': 'Mathématiques de l\'assurance',
                    'description': 'Techniques actuarielle vie et non-vie, tarification et provisions',
                    'credits': 6,
                    'coefficient': 2,
                    'cycle': 'licence',
                    'niveau': 'L2',
                    'semestre': 1,
                    'filiere_code': 'ARISK'
                },
                {
                    'code': 'APRED301',
                    'intitule': 'Apprentissage statistique',
                    'description': 'Méthodes de prédiction et modélisation supervisée pour l\'actuariat',
                    'credits': 5,
                    'coefficient': 2,
                    'cycle': 'licence',
                    'niveau': 'L3',
                    'semestre': 1,
                    'filiere_code': 'APRED'
                },
                {
                    'code': 'SECO210',
                    'intitule': 'Politiques macroéconomiques',
                    'description': 'Analyse des politiques budgétaires et monétaires appuyée par la statistique',
                    'credits': 4,
                    'coefficient': 1.5,
                    'cycle': 'licence',
                    'niveau': 'L2',
                    'semestre': 2,
                    'filiere_code': 'SECO'
                },
                {
                    'code': 'SDATA320',
                    'intitule': 'Informatique décisionnelle',
                    'description': 'Entreposage de données, ETL et tableaux de bord pour la data science',
                    'credits': 5,
                    'coefficient': 2,
                    'cycle': 'licence',
                    'niveau': 'L3',
                    'semestre': 2,
                    'filiere_code': 'SDATA'
                },
                {
                    'code': 'PROB330',
                    'intitule': 'Processus aléatoires avancés',
                    'description': 'Processus stochastiques, martingales et applications industrielles',
                    'credits': 6,
                    'coefficient': 2,
                    'cycle': 'licence',
                    'niveau': 'L3',
                    'semestre': 2,
                    'filiere_code': 'PROBSTATS'
                },
                {
                    'code': 'MACTU510',
                    'intitule': 'Gestion actif-passif',
                    'description': 'Optimisation des portefeuilles et gestion des risques pour assureurs',
                    'credits': 6,
                    'coefficient': 2,
                    'cycle': 'master',
                    'niveau': 'M1',
                    'semestre': 1,
                    'filiere_code': 'MACTU'
                },
                {
                    'code': 'MSAID520',
                    'intitule': 'Architecture BI & Big Data',
                    'description': 'Conception de plateformes décisionnelles et exploitation des données massives',
                    'credits': 5,
                    'coefficient': 2,
                    'cycle': 'master',
                    'niveau': 'M1',
                    'semestre': 1,
                    'filiere_code': 'MSAID'
                },
                {
                    'code': 'MMSP530',
                    'intitule': 'Théorie avancée des probabilités',
                    'description': 'Base mathématique pour la modélisation statistique et la recherche',
                    'credits': 5,
                    'coefficient': 2,
                    'cycle': 'master',
                    'niveau': 'M1',
                    'semestre': 1,
                    'filiere_code': 'MMSP'
                }
            ]
            for ue_data in ues:
                if not UniteEnseignement.query.filter_by(code=ue_data['code']).first():
                    filiere = filieres_map.get(ue_data['filiere_code']) or Filiere.query.filter_by(code=ue_data['filiere_code']).first()
                    ue = UniteEnseignement(
                        code=ue_data['code'],
                        intitule=ue_data['intitule'],
                        description=ue_data['description'],
                        credits=ue_data['credits'],
                        coefficient=ue_data['coefficient'],
                        cycle=ue_data['cycle'],
                        niveau=ue_data['niveau'],
                        semestre=ue_data['semestre'],
                        filiere_id=filiere.id if filiere else None,
                        volume_cm=30,
                        volume_td=20,
                        volume_tp=10,
                        type_ue='fondamentale',
                        nature='obligatoire',
                        annee_academique=annee_courante,
                        est_capitalizable=True,
                        est_active=True
                    )
                    db.session.add(ue)
                    print(f"  ✓ UE créée: {ue_data['code']} - {ue_data['intitule']}")
                else:
                    print(f"  - UE existante: {ue_data['code']}")
            db.session.commit()

            print("✅ Données de base initialisées avec succès!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de l'initialisation: {e}")
            raise

if __name__ == '__main__':
    init_base_data()
