import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

class ModeleRisqueCredit:
    """
    Modèle simple d'IA pour prédire si un client va rembourser son crédit
    
    Ce modèle utilise l'apprentissage automatique pour dire si un client
    est susceptible de rembourser (0) ou de ne pas rembourser (1) son crédit.
    """
    
    def __init__(self):
        """Initialise le modèle"""
        self.modele_ia = RandomForestClassifier(n_estimators=50, random_state=42)
        self.encodeurs = {}  # Pour encoder les variables catégorielles
        self.est_entraine = False
        print("🤖 Modèle créé ! Prêt pour l'entraînement.")
    
    def creer_donnees_exemple(self, nombre_clients=1000):
        """
        Crée des données d'exemple pour entraîner notre modèle
        
        Args:
            nombre_clients: Combien de clients fictifs créer
            
        Returns:
            Un tableau avec les données des clients
        """
        print(f"📊 Création de {nombre_clients} clients fictifs...")
        
        # On génère des données aléatoires mais réalistes
        np.random.seed(42)  # Pour avoir toujours les mêmes résultats
        
        donnees_clients = {
            # Informations personnelles
            'age_client': np.random.randint(18, 70, nombre_clients),
            'salaire_annuel': np.random.randint(20000, 100000, nombre_clients),
            'annees_emploi': np.random.randint(0, 30, nombre_clients),
            
            # Nouvelles données sociodémographiques
            'niveau_education': np.random.choice(['Secondaire', 'Licence', 'Master', 'Doctorat'], nombre_clients),
            'statut_emploi': np.random.choice(['Salarié', 'Indépendant', 'Sans emploi'], nombre_clients, p=[0.7, 0.25, 0.05]),
            'situation_familiale': np.random.choice(['Célibataire', 'Marié(e)', 'Divorcé(e)'], nombre_clients, p=[0.4, 0.5, 0.1]),
            'type_logement': np.random.choice(['Propriétaire', 'Locataire', 'Emprunteur'], nombre_clients, p=[0.3, 0.4, 0.3]),
            'objectif_credit': np.random.choice(['Personnel', 'Auto', 'Immobilier', 'Professionnel', 'Éducation'], nombre_clients),
            
            # Informations sur le crédit demandé
            'montant_credit': np.random.randint(5000, 80000, nombre_clients),
            'duree_mois': np.random.choice([12, 24, 36, 48, 60], nombre_clients),
            
            # Historique financier
            'score_credit': np.random.randint(300, 850, nombre_clients),
            'nombre_cartes': np.random.randint(0, 8, nombre_clients),
            'credits_precedents': np.random.randint(0, 5, nombre_clients),
        }
        
        # On convertit en DataFrame (tableau)
        tableau_clients = pd.DataFrame(donnees_clients)
        
        # On crée une règle plus complexe pour déterminer qui va faire défaut
        # en tenant compte des nouvelles variables
        risque_defaut = (
            (tableau_clients['score_credit'] < 600) * 0.4 +  # Score faible = risque
            (tableau_clients['salaire_annuel'] < 30000) * 0.2 +  # Salaire faible = risque
            (tableau_clients['montant_credit'] > tableau_clients['salaire_annuel'] * 0.8) * 0.3 +  # Crédit trop gros = risque
            (tableau_clients['statut_emploi'] == 'Sans emploi') * 0.8 +  # Sans emploi = très risqué
            (tableau_clients['statut_emploi'] == 'Indépendant') * 0.2 +  # Indépendant = un peu plus risqué
            (tableau_clients['situation_familiale'] == 'Divorcé(e)') * 0.15 +  # Divorce = petit risque
            (tableau_clients['type_logement'] == 'Locataire') * 0.1 +  # Locataire = petit risque
            (tableau_clients['objectif_credit'] == 'Personnel') * 0.1 +  # Crédit personnel = petit risque
            (tableau_clients['niveau_education'] == 'Secondaire') * 0.1 +  # Éducation faible = petit risque
            np.random.random(nombre_clients) * 0.15  # Un peu d'aléatoire
        )
        
        # 0 = va rembourser, 1 = va faire défaut
        tableau_clients['va_faire_defaut'] = (risque_defaut > 0.5).astype(int)
        
        pourcentage_defaut = tableau_clients['va_faire_defaut'].mean() * 100
        print(f"✅ Données créées ! {pourcentage_defaut:.1f}% des clients vont faire défaut.")
        
        # Sauvegarde automatique en Excel
        try:
            nom_fichier = f"donnees_clients_{nombre_clients}.xlsx"
            tableau_clients.to_excel(nom_fichier, index=False, engine='openpyxl')
            print(f"💾 Données sauvegardées dans : {nom_fichier}")
        except ImportError:
            print("⚠️ Pour sauvegarder en Excel, installez : pip install openpyxl")
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde Excel : {e}")
        
        return tableau_clients
    
    def encoder_variables_categorielles(self, donnees):
        """
        Encode les variables catégorielles en nombres pour le modèle IA
        
        Args:
            donnees: DataFrame avec les données
            
        Returns:
            DataFrame avec les variables encodées
        """
        donnees_encodees = donnees.copy()
        
        # Variables catégorielles à encoder
        variables_cat = ['niveau_education', 'statut_emploi', 'situation_familiale', 
                        'type_logement', 'objectif_credit']
        
        for variable in variables_cat:
            if variable in donnees_encodees.columns:
                if variable not in self.encodeurs:
                    # Créer un nouvel encodeur pour cette variable
                    self.encodeurs[variable] = LabelEncoder()
                    donnees_encodees[variable] = self.encodeurs[variable].fit_transform(donnees_encodees[variable])
                else:
                    # Utiliser l'encodeur existant
                    donnees_encodees[variable] = self.encodeurs[variable].transform(donnees_encodees[variable])
        
        return donnees_encodees
    
    def entrainer_modele(self, donnees_clients):
        """
        Entraîne notre modèle IA avec les données des clients
        
        Args:
            donnees_clients: Tableau avec les informations des clients
        """
        print("🎓 Début de l'entraînement du modèle...")
        
        # Encoder les variables catégorielles
        donnees_encodees = self.encoder_variables_categorielles(donnees_clients)
        
        # On sépare les caractéristiques (X) de ce qu'on veut prédire (y)
        caracteristiques_clients = donnees_encodees.drop('va_faire_defaut', axis=1)  # Toutes les colonnes sauf la cible
        resultat_a_predire = donnees_encodees['va_faire_defaut']  # Ce qu'on veut prédire
        
        # On divise les données : 80% pour entraîner, 20% pour tester
        X_entrainement, X_test, y_entrainement, y_test = train_test_split(
            caracteristiques_clients, 
            resultat_a_predire, 
            test_size=0.2,  # 20% pour les tests
            random_state=42
        )
        
        print(f"📚 Entraînement avec {len(X_entrainement)} clients")
        print(f"🧪 Test avec {len(X_test)} clients")
        
        # On entraîne notre modèle IA
        self.modele_ia.fit(X_entrainement, y_entrainement)
        
        # On teste la précision
        predictions_test = self.modele_ia.predict(X_test)
        precision = accuracy_score(y_test, predictions_test)
        
        self.est_entraine = True
        print(f"✅ Entraînement terminé ! Précision : {precision:.1%}")
        
        # Afficher l'importance des variables
        self.afficher_importance_variables(caracteristiques_clients.columns)
        
        return precision
    
    def afficher_importance_variables(self, noms_colonnes):
        """Affiche l'importance de chaque variable dans la prédiction"""
        if hasattr(self.modele_ia, 'feature_importances_'):
            importances = self.modele_ia.feature_importances_
            indices_tries = np.argsort(importances)[::-1]
            
            print("\n📊 IMPORTANCE DES VARIABLES :")
            print("-" * 40)
            for i in range(min(8, len(indices_tries))):  # Top 8 variables
                idx = indices_tries[i]
                print(f"{i+1}. {noms_colonnes[idx]}: {importances[idx]:.3f}")
    
    def predire_risque_client(self, infos_client):
        """
        Prédit si un client va faire défaut ou non
        
        Args:
            infos_client: Dictionnaire avec les infos du client
            
        Returns:
            Prédiction et probabilité de défaut
        """
        if not self.est_entraine:
            print("❌ Erreur : Le modèle n'est pas encore entraîné !")
            return None
        
        # On retire le nom du client (pas utilisé pour la prédiction)
        infos_pour_prediction = infos_client.copy()
        if 'nom' in infos_pour_prediction:
            del infos_pour_prediction['nom']
        
        # On convertit les infos en format que le modèle comprend
        client_dataframe = pd.DataFrame([infos_pour_prediction])
        
        # Encoder les variables catégorielles
        client_encode = self.encoder_variables_categorielles(client_dataframe)
        
        # Prédiction : 0 ou 1
        prediction = self.modele_ia.predict(client_encode)[0]
        
        # Probabilité de faire défaut (entre 0 et 1)
        probabilite_defaut = self.modele_ia.predict_proba(client_encode)[0][1]
        
        return {
            'va_faire_defaut': prediction,
            'probabilite_defaut': probabilite_defaut,
            'niveau_risque': self.classifier_risque(probabilite_defaut),
            'recommandation': self.donner_recommandation(probabilite_defaut)
        }
    
    def classifier_risque(self, probabilite):
        """Classe le niveau de risque selon la probabilité"""
        if probabilite < 0.3:
            return "🟢 FAIBLE"
        elif probabilite < 0.6:
            return "🟡 MOYEN"
        else:
            return "🔴 ÉLEVÉ"
    
    def donner_recommandation(self, probabilite):
        """Donne une recommandation selon le risque"""
        if probabilite < 0.3:
            return "✅ APPROUVER le crédit"
        elif probabilite < 0.6:
            return "⚠️ EXAMINER plus en détail"
        else:
            return "❌ REFUSER le crédit"
    
    def sauvegarder_donnees_excel(self, donnees, nom_fichier="donnees_clients.xlsx"):
        """
        Sauvegarde les données dans un fichier Excel
        
        Args:
            donnees: DataFrame à sauvegarder
            nom_fichier: Nom du fichier Excel
        """
        try:
            # Ajout de colonnes explicatives en français
            donnees_avec_labels = donnees.copy()
            
            # Renommage des colonnes pour plus de clarté
            colonnes_francais = {
                'age_client': 'Âge du client',
                'salaire_annuel': 'Salaire annuel (€)',
                'annees_emploi': 'Années d\'emploi',
                'niveau_education': 'Niveau d\'éducation',
                'statut_emploi': 'Statut d\'emploi',
                'situation_familiale': 'Situation familiale',
                'type_logement': 'Type de logement',
                'objectif_credit': 'Objectif du crédit',
                'montant_credit': 'Montant crédit demandé (€)',
                'duree_mois': 'Durée remboursement (mois)',
                'score_credit': 'Score de crédit (300-850)',
                'nombre_cartes': 'Nombre cartes de crédit',
                'credits_precedents': 'Crédits précédents',
                'va_faire_defaut': 'Va faire défaut (1=Oui, 0=Non)'
            }
            
            donnees_avec_labels = donnees_avec_labels.rename(columns=colonnes_francais)
            
            # Sauvegarde en Excel avec formatage
            with pd.ExcelWriter(nom_fichier, engine='openpyxl') as writer:
                donnees_avec_labels.to_excel(writer, sheet_name='Données Clients', index=False)
                
                # Accès au workbook pour le formatage
                workbook = writer.book
                worksheet = writer.sheets['Données Clients']
                
                # Ajustement automatique de la largeur des colonnes
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"💾 ✅ Fichier Excel créé avec succès : {nom_fichier}")
            print(f"📊 Contient {len(donnees)} lignes de données")
            
        except ImportError:
            print("❌ Pour créer des fichiers Excel, installez :")
            print("   pip install openpyxl")
        except Exception as e:
            print(f"❌ Erreur lors de la création du fichier Excel : {e}")
    
    def analyser_client(self, infos_client):
        """
        Analyse complète d'un client avec explications
        """
        print("🔍 Analyse du client en cours...")
        
        resultat = self.predire_risque_client(infos_client)
        
        if resultat is None:
            return
        
        print("\n" + "="*50)
        print("📊 RÉSULTAT DE L'ANALYSE")
        print("="*50)
        print(f"Client : {infos_client.get('nom', 'Anonyme')}")
        print(f"Âge : {infos_client['age_client']} ans")
        print(f"Salaire : {infos_client['salaire_annuel']:,} €/an")
        print(f"Statut emploi : {infos_client['statut_emploi']}")
        print(f"Éducation : {infos_client['niveau_education']}")
        print(f"Situation familiale : {infos_client['situation_familiale']}")
        print(f"Type logement : {infos_client['type_logement']}")
        print(f"Objectif crédit : {infos_client['objectif_credit']}")
        print(f"Crédit demandé : {infos_client['montant_credit']:,} €")
        print(f"Score de crédit : {infos_client['score_credit']}")
        print("-"*50)
        print(f"🎯 Probabilité de défaut : {resultat['probabilite_defaut']:.1%}")
        print(f"📈 Niveau de risque : {resultat['niveau_risque']}")
        print(f"💼 Recommandation : {resultat['recommandation']}")
        print("="*50)
        
        return resultat


# ========================================
# EXEMPLE D'UTILISATION SIMPLE
# ========================================

def exemple_utilisation():
    """
    Exemple simple d'utilisation du modèle
    """
    print("🏦 EXEMPLE D'UTILISATION - MODÈLE DE RISQUE DE CRÉDIT AMÉLIORÉ")
    print("="*65)
    
    # 1. Créer le modèle
    mon_modele = ModeleRisqueCredit()
    
    # 2. Créer des données d'exemple
    donnees_exemple = mon_modele.creer_donnees_exemple(nombre_clients=2000)
    
    # 3. Entraîner le modèle
    precision = mon_modele.entrainer_modele(donnees_exemple)
    
    # 3.5. Sauvegarder les données en Excel
    print("\n💾 SAUVEGARDE DES DONNÉES")
    print("-"*40)
    mon_modele.sauvegarder_donnees_excel(
        donnees_exemple, 
        f"donnees_entrainement_{len(donnees_exemple)}_clients.xlsx"
    )
    
    # 4. Tester avec des clients fictifs
    print("\n🧪 TEST AVEC DES CLIENTS FICTIFS")
    print("-"*40)
    
    # Client avec un bon profil
    client_bon_profil = {
        'nom': 'Marie Dupont',
        'age_client': 35,
        'salaire_annuel': 55000,
        'annees_emploi': 8,
        'niveau_education': 'Master',
        'statut_emploi': 'Salarié',
        'situation_familiale': 'Marié(e)',
        'type_logement': 'Propriétaire',
        'objectif_credit': 'Immobilier',
        'montant_credit': 25000,
        'duree_mois': 36,
        'score_credit': 720,
        'nombre_cartes': 2,
        'credits_precedents': 1
    }
    
    # Client avec un profil risqué
    client_profil_risque = {
        'nom': 'Paul Martin',
        'age_client': 28,
        'salaire_annuel': 28000,
        'annees_emploi': 2,
        'niveau_education': 'Secondaire',
        'statut_emploi': 'Indépendant',
        'situation_familiale': 'Divorcé(e)',
        'type_logement': 'Locataire',
        'objectif_credit': 'Personnel',
        'montant_credit': 45000,
        'duree_mois': 72,
        'score_credit': 580,
        'nombre_cartes': 5,
        'credits_precedents': 3
    }
    
    # Analyser les deux clients
    print("\n👤 ANALYSE CLIENT 1 :")
    mon_modele.analyser_client(client_bon_profil)
    
    print("\n👤 ANALYSE CLIENT 2 :")
    mon_modele.analyser_client(client_profil_risque)
    
    return mon_modele


def tester_votre_client():
    """
    Fonction pour tester avec vos propres données
    """
    print("\n🔧 TESTEZ VOTRE PROPRE CLIENT")
    print("-"*40)
    print("Entrez les informations du client (ou appuyez sur Entrée pour valeur par défaut) :")
    
    # Demander les infos à l'utilisateur
    try:
        infos_client = {
            'nom': input("Nom du client : ") or "Client Test",
            'age_client': int(input("Âge (défaut 30) : ") or 30),
            'salaire_annuel': int(input("Salaire annuel en € (défaut 40000) : ") or 40000),
            'annees_emploi': int(input("Années d'emploi (défaut 5) : ") or 5),
            'niveau_education': input("Niveau éducation (Secondaire/Licence/Master/Doctorat, défaut Licence) : ") or "Licence",
            'statut_emploi': input("Statut emploi (Salarié/Indépendant/Sans emploi, défaut Salarié) : ") or "Salarié",
            'situation_familiale': input("Situation familiale (Célibataire/Marié(e)/Divorcé(e), défaut Célibataire) : ") or "Célibataire",
            'type_logement': input("Type logement (Propriétaire/Locataire/Emprunteur, défaut Locataire) : ") or "Locataire",
            'objectif_credit': input("Objectif crédit (Personnel/Auto/Immobilier/Professionnel/Éducation, défaut Personnel) : ") or "Personnel",
            'montant_credit': int(input("Montant du crédit demandé en € (défaut 30000) : ") or 30000),
            'duree_mois': int(input("Durée en mois (défaut 36) : ") or 36),
            'score_credit': int(input("Score de crédit 300-850 (défaut 650) : ") or 650),
            'nombre_cartes': int(input("Nombre de cartes de crédit (défaut 2) : ") or 2),
            'credits_precedents': int(input("Nombre de crédits précédents (défaut 1) : ") or 1)
        }
        
        return infos_client
    
    except ValueError:
        print("❌ Erreur dans la saisie, utilisation des valeurs par défaut")
        return {
            'nom': "Client Test",
            'age_client': 30,
            'salaire_annuel': 40000,
            'annees_emploi': 5,
            'niveau_education': "Licence",
            'statut_emploi': "Salarié",
            'situation_familiale': "Célibataire",
            'type_logement': "Locataire",
            'objectif_credit': "Personnel",
            'montant_credit': 30000,
            'duree_mois': 36,
            'score_credit': 650,
            'nombre_cartes': 2,
            'credits_precedents': 1
        }


# ========================================
# PROGRAMME PRINCIPAL
# ========================================

if __name__ == "__main__":
    # Lancer l'exemple
    modele_entraine = exemple_utilisation()
    
    # Proposer un test interactif
    print("\n" + "="*60)
    print("🎮 VOULEZ-VOUS TESTER VOTRE PROPRE CLIENT ?")
    print("="*60)
    
    reponse = input("Tapez 'oui' pour tester votre client ou Entrée pour terminer : ")
    
    if reponse.lower() in ['oui', 'o', 'yes', 'y']:
        client_test = tester_votre_client()
        modele_entraine.analyser_client(client_test)
    
    print("\n🎉 Démonstration terminée !")
    print("💡 Ce modèle amélioré prend en compte plus de facteurs sociodémographiques.")
    print("📚 Pour aller plus loin, étudiez les algorithmes de machine learning !")