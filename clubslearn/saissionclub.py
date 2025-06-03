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
    
    def creer_donnees_exemple(self, nombre_clients=500):
        """
        Crée des données d'exemple pour entraîner notre modèle
        """
        print(f"📊 Création de {nombre_clients} clients fictifs...")
        
        # On génère des données aléatoires mais réalistes
        np.random.seed(42)  # Pour avoir toujours les mêmes résultats
        
        donnees_clients = {
            # Informations personnelles
            'age_client': np.random.randint(18, 70, nombre_clients),
            'salaire_annuel': np.random.randint(2000000, 10000000, nombre_clients),
            'annees_emploi': np.random.randint(0, 30, nombre_clients),
            
            # Informations sur le crédit demandé
            'montant_credit': np.random.randint(500000, 8000000, nombre_clients),
            'duree_mois': np.random.choice([12, 24, 36, 48, 60], nombre_clients),
            
            # Historique financier
            'score_credit': np.random.randint(300, 850, nombre_clients),
            'nombre_cartes': np.random.randint(0, 8, nombre_clients),
        }
        
        # On convertit en DataFrame (tableau)
        tableau_clients = pd.DataFrame(donnees_clients)
        
        # Règle simple : si 2 conditions ou plus sont vraies, c'est risqué
        conditions_risque = (
            (tableau_clients['score_credit'] < 650) +  # Score faible (augmenté)
            (tableau_clients['salaire_annuel'] < 4000000) +  # Salaire faible
            (tableau_clients['montant_credit'] > 4000000) +  # Crédit élevé (réduit)
            (tableau_clients['annees_emploi'] < 3) +  # Peu d'expérience
            (tableau_clients['nombre_cartes'] > 4)  # Trop de cartes
        )
        
        # 0 = va rembourser, 1 = va faire défaut
        # Si 2 conditions ou plus sont vraies = défaut
        tableau_clients['va_faire_defaut'] = (conditions_risque >= 2).astype(int)
        
        pourcentage_defaut = tableau_clients['va_faire_defaut'].mean() * 100
        print(f"✅ Données créées ! {pourcentage_defaut:.1f}% des clients vont faire défaut.")
        
        return tableau_clients
    
    def entrainer_modele(self, donnees_clients):
        """
        Entraîne notre modèle IA avec les données des clients
        """
        print("🎓 Début de l'entraînement du modèle...")
        
        # On sépare les caractéristiques (X) de ce qu'on veut prédire (y)
        caracteristiques_clients = donnees_clients.drop('va_faire_defaut', axis=1)
        resultat_a_predire = donnees_clients['va_faire_defaut']
        
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
        """
        if not self.est_entraine:
            print("❌ Erreur : Le modèle n'est pas encore entraîné !")
            return None
        
        # On convertit les infos en format que le modèle comprend
        client_dataframe = pd.DataFrame([infos_client])
        
        # Prédiction : 0 ou 1
        prediction = self.modele_ia.predict(client_dataframe)[0]
        
        # Probabilité de faire défaut (entre 0 et 1)
        # Vérifier si le modèle a appris les deux classes
        proba_classes = self.modele_ia.predict_proba(client_dataframe)[0]
        if len(proba_classes) == 2:
            probabilite_defaut = proba_classes[1]  # Probabilité de la classe 1 (défaut)
        else:
            # Si une seule classe, probabilité basée sur la prédiction
            probabilite_defaut = float(prediction)
        
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
        print(f"Âge : {infos_client['age_client']} ans")
        print(f"Salaire : {infos_client['salaire_annuel']:,} BIF/an")
        print(f"Années d'emploi : {infos_client['annees_emploi']} ans")
        print(f"Crédit demandé : {infos_client['montant_credit']:,} BIF")
        print(f"Score de crédit : {infos_client['score_credit']}")
        print("-"*50)
        print(f"🎯 Probabilité de défaut : {resultat['probabilite_defaut']:.1%}")
        print(f"📈 Niveau de risque : {resultat['niveau_risque']}")
        print(f"💼 Recommandation : {resultat['recommandation']}")
        print("="*50)
        
        return resultat


def exemple_utilisation():
    """
    Exemple simple d'utilisation du modèle
    """
    print("🏦 EXEMPLE D'UTILISATION - MODÈLE DE RISQUE DE CRÉDIT")
    print("="*55)
    
    # 1. Créer le modèle
    mon_modele = ModeleRisqueCredit()
    
    # 2. Créer des données d'exemple
    donnees_exemple = mon_modele.creer_donnees_exemple(nombre_clients=500)
    
    # 3. Entraîner le modèle
    precision = mon_modele.entrainer_modele(donnees_exemple)
    
    # 4. Tester avec des clients fictifs
    print("\n🧪 TEST AVEC DES CLIENTS FICTIFS")
    print("-"*40)
    
    # Client avec un bon profil - Fleury Niyokwizera
    client_bon_profil = {
        'age_client': 35,
        'salaire_annuel': 5500000,  # 5.5M BIF/an
        'annees_emploi': 8,
        'montant_credit': 2500000,  # 2.5M BIF
        'duree_mois': 36,
        'score_credit': 720,
        'nombre_cartes': 2
    }
    
    # Client avec un profil risqué - Bucumi Jean
    client_profil_risque = {
        'age_client': 28,
        'salaire_annuel': 2800000,  # 2.8M BIF/an
        'annees_emploi': 1,
        'montant_credit': 4500000,  # 4.5M BIF
        'duree_mois': 72,
        'score_credit': 580,
        'nombre_cartes': 5
    }
    
    # Analyser les deux clients
    print("\n👤 ANALYSE CLIENT 1 - Fleury Niyokwizera (Bon profil) :")
    mon_modele.analyser_client(client_bon_profil)
    
    print("\n👤 ANALYSE CLIENT 2 - Bucumi Jean (Profil risqué) :")
    mon_modele.analyser_client(client_profil_risque)
    
    return mon_modele


def tester_votre_client():
    """
    Fonction pour tester avec vos propres données
    """
    print("\n🔧 TESTEZ VOTRE PROPRE CLIENT")
    print("-"*40)
    print("Entrez les informations du client :")
    
    try:
        infos_client = {
            'age_client': int(input("Âge du client : ")),
            'salaire_annuel': int(input("Salaire annuel en BIF (ex: 4000000) : ")),
            'annees_emploi': int(input("Années d'emploi : ")),
            'montant_credit': int(input("Montant du crédit demandé en BIF (ex: 2000000) : ")),
            'duree_mois': int(input("Durée en mois (12, 24, 36, 48, 60) : ")),
            'score_credit': int(input("Score de crédit (300-850) : ")),
            'nombre_cartes': int(input("Nombre de cartes de crédit : "))
        }
        
        return infos_client
    
    except ValueError:
        print("❌ Erreur dans la saisie. Utilisez des nombres uniquement.")
        return None


def montrer_exemples_detailles():
    """
    Montre des exemples détaillés de profils à défaut et sans défaut
    """
    print("\n📚 EXEMPLES DÉTAILLÉS DE PROFILS")
    print("="*50)
    
    print("\n🟢 PROFIL SANS DÉFAUT (Faible risque):")
    print("-"*40)
    print("• Âge : 35-45 ans (expérience de vie)")
    print("• Salaire : > 4M BIF/an (bon revenu)")
    print("• Emploi : > 3 ans (stabilité)")
    print("• Crédit : < 4M BIF (montant raisonnable)")
    print("• Score : > 650 (bon historique)")
    print("• Cartes : ≤ 4 (gestion modérée)")
    
    print("\n🔴 PROFIL À DÉFAUT (Risque élevé):")
    print("-"*40)
    print("• Âge : 18-25 ans (peu d'expérience)")
    print("• Salaire : < 4M BIF/an (revenu faible)")
    print("• Emploi : < 3 ans (instabilité)")
    print("• Crédit : > 4M BIF (montant élevé)")
    print("• Score : < 650 (historique moyen/faible)")
    print("• Cartes : > 4 (sur-endettement)")
    
    print("\n⚖️ RÈGLE DE DÉCISION:")
    print("Si 2 critères de risque ou plus = DÉFAUT probable")


# ========================================
# PROGRAMME PRINCIPAL
# ========================================

if __name__ == "__main__":
    # Lancer l'exemple
    modele_entraine = exemple_utilisation()
    
    # Montrer les exemples détaillés
    montrer_exemples_detailles()
    
    # Proposer un test interactif
    print("\n" + "="*60)
    print("🎮 VOULEZ-VOUS TESTER VOTRE PROPRE CLIENT ?")
    print("="*60)
    
    reponse = input("Tapez 'oui' pour tester un client ou Entrée pour terminer : ")
    
    if reponse.lower() in ['oui', 'o', 'yes', 'y']:
        client_test = tester_votre_client()
        if client_test:
            print("\n👤 ANALYSE DE VOTRE CLIENT :")
            modele_entraine.analyser_client(client_test)
        else:
            print("❌ Test annulé à cause d'erreurs de saisie.")
    
    print("\n🎉 Démonstration terminée !")
    print("💡 Ce modèle analyse 7 critères simples pour évaluer le risque de crédit au Burundi.")
    print("📚 Montants en Francs Burundais (BIF) - Salaires typiques : 2-10M BIF/an")
    print("🏦 Pour aller plus loin, étudiez les algorithmes de machine learning !")