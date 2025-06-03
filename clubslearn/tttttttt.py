import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
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
        
        # On crée une règle simple pour déterminer qui va faire défaut
        # Plus le score est bas, plus le risque est élevé
        risque_defaut = (
            (tableau_clients['score_credit'] < 600) * 0.6 +  # Score faible = risque
            (tableau_clients['salaire_annuel'] < 30000) * 0.3 +  # Salaire faible = risque
            (tableau_clients['montant_credit'] > tableau_clients['salaire_annuel'] * 0.8) * 0.4 +  # Crédit trop gros = risque
            np.random.random(nombre_clients) * 0.2  # Un peu d'aléatoire
        )
        
        # 0 = va rembourser, 1 = va faire défaut
        tableau_clients['va_faire_defaut'] = (risque_defaut > 0.5).astype(int)
        
        pourcentage_defaut = tableau_clients['va_faire_defaut'].mean() * 100
        print(f"✅ Données créées ! {pourcentage_defaut:.1f}% des clients vont faire défaut.")
        
        # Sauvegarde automatique en ODS (LibreOffice Calc)
        try:
            nom_fichier = f"donnees_clients_{nombre_clients}.ods"
            tableau_clients.to_excel(nom_fichier, index=False, engine='odf')
            print(f"💾 Données sauvegardées dans : {nom_fichier}")
        except ImportError:
            print("⚠️ Pour sauvegarder en ODS, installez : pip install odfpy")
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde ODS : {e}")
        
        return tableau_clients
    
    def entrainer_modele(self, donnees_clients):
        """
        Entraîne notre modèle IA avec les données des clients
        
        Args:
            donnees_clients: Tableau avec les informations des clients
        """
        print("🎓 Début de l'entraînement du modèle...")
        
        # On sépare les caractéristiques (X) de ce qu'on veut prédire (y)
        caracteristiques_clients = donnees_clients.drop('va_faire_defaut', axis=1)  # Toutes les colonnes sauf la cible
        resultat_a_predire = donnees_clients['va_faire_defaut']  # Ce qu'on veut prédire
        
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
        
        return precision
    
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
        
        # Prédiction : 0 ou 1
        prediction = self.modele_ia.predict(client_dataframe)[0]
        
        # Probabilité de faire défaut (entre 0 et 1)
        probabilite_defaut = self.modele_ia.predict_proba(client_dataframe)[0][1]
        
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
    
    def sauvegarder_donnees_ods(self, donnees, nom_fichier="donnees_clients.ods"):
        """
        Sauvegarde les données dans un fichier ODS (LibreOffice Calc)
        
        Args:
            donnees: DataFrame à sauvegarder
            nom_fichier: Nom du fichier ODS
        """
        try:
            # Ajout de colonnes explicatives en français
            donnees_avec_labels = donnees.copy()
            
            # Renommage des colonnes pour plus de clarté
            colonnes_francais = {
                'age_client': 'Âge du client',
                'salaire_annuel': 'Salaire annuel (€)',
                'annees_emploi': 'Années d\'emploi',
                'montant_credit': 'Montant crédit demandé (€)',
                'duree_mois': 'Durée remboursement (mois)',
                'score_credit': 'Score de crédit (300-850)',
                'nombre_cartes': 'Nombre cartes de crédit',
                'credits_precedents': 'Crédits précédents',
                'va_faire_defaut': 'Va faire défaut (1=Oui, 0=Non)'
            }
            
            donnees_avec_labels = donnees_avec_labels.rename(columns=colonnes_francais)
            
            # Sauvegarde en ODS
            donnees_avec_labels.to_excel(nom_fichier, index=False, engine='odf')
            
            print(f"💾 ✅ Fichier ODS créé avec succès : {nom_fichier}")
            print(f"📊 Contient {len(donnees)} lignes de données")
            print(f"🖥️ Ouvrez le fichier avec LibreOffice Calc")
            
        except ImportError:
            print("❌ Pour créer des fichiers ODS, installez :")
            print("   pip install odfpy")
            print("   ou utilisez : sudo apt install python3-odf")
        except Exception as e:
            print(f"❌ Erreur lors de la création du fichier ODS : {e}")
            # Fallback vers CSV si ODS ne fonctionne pas
            nom_csv = nom_fichier.replace('.ods', '.csv')
            try:
                donnees_avec_labels.to_csv(nom_csv, index=False, encoding='utf-8')
                print(f"💾 Fichier CSV créé en alternative : {nom_csv}")
            except Exception as e2:
                print(f"❌ Erreur CSV également : {e2}")
    
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
    print("🏦 EXEMPLE D'UTILISATION - MODÈLE DE RISQUE DE CRÉDIT")
    print("="*60)
    
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
    print("💡 Ce modèle simple vous montre les bases de l'IA pour la finance.")
    print("📚 Pour aller plus loin, étudiez les algorithmes de machine learning !")