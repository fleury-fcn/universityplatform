'''
Implementation du modele de risque de credit dans une Banque
'''

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings("ignore")


class ModelCreditRisk:

    def __init__(self):
        self.modele_ai = RandomForestClassifier(n_estimators=50, random_state=42)
        self.is_trained = False

    def Creer_donnees_clients(self, n_clients=1000):

        print(f'Generation de {n_clients} donnees clients')

        np.random.seed(42)

        donnes_clients = {
            # Information sur le client
            'age': np.random.randint(18, 80, size=n_clients),
            'revenu_annuel': np.random.randint(2000000, 10000000, size=n_clients),
            'mois_emploi': np.random.randint(0, 40, size=n_clients),

            # Information sur le montant cherche 
            'montant_cherche': np.random.randint(1000000, 6000000, size=n_clients),
            'duree_remboursement': np.random.choice([12, 24, 36, 48, 60], size=n_clients),

            # Historique de credits
            'nombre_credit_en_cours': np.random.randint(0, 5, size=n_clients),
            'score_credit': np.random.randint(300, 850, size=n_clients),
        }

        # Convertir en DataFrame
        df_clients = pd.DataFrame(donnes_clients)

        # Conditions de risque, si au moins deux conditions sont verifiees, le client est risque
        conditions_risque = (
            (df_clients['revenu_annuel'] < 4000000) +  # Revenue annuel faible
            (df_clients['mois_emploi'] < 24) +  # Mois d'emploi faible
            (df_clients['montant_cherche'] > 4000000) +  # Montant demandé élevé (corrigé)
            (df_clients['nombre_credit_en_cours'] > 3)
        )

        df_clients['va_faire_defaut'] = (conditions_risque >= 2).astype(int)

        # Afficher les 10 premiers clients
        print(df_clients.head(10))

        # Pourcentage des clients Risques
        pourcentage_risque = df_clients['va_faire_defaut'].mean() * 100
        print(f'Pourcentage des clients risques : {pourcentage_risque:.2f}%')
        
        return df_clients
    
    def Entrainer_modele(self, df_clients):  
        # Diviser les donnees en X et Y 
        # Y est la variable cible

        features = df_clients.drop('va_faire_defaut', axis=1)
        target = df_clients['va_faire_defaut']

        # Diviser les donnees d'entrainement et les donnees de test 80% pour entrainer et 20% tester
        x_train, x_test, y_train, y_test = train_test_split(  # Corrigé: x_text -> x_test
            features,
            target,
            test_size=0.2,
            random_state=42
        )

        # Entrainer le modele alors
        self.modele_ai.fit(x_train, y_train)

        # Verifier la prediction et la precision du modele
        predictions_test = self.modele_ai.predict(x_test)  # Corrigé: x_text -> x_test
        precision_test = accuracy_score(y_test, predictions_test)

        self.is_trained = True
        print(f"La precision du modele est : {precision_test:.1%}")

        return precision_test
    
    def predire_risque_client(self, infos_clients):
        '''
        Predire si un client presente un defaut ou non
        '''
        # Verifier si un model est entraine ou non
        if not self.is_trained:
            print("Le modele n'est pas entraine")
            return None

        # Convertir dans une forme acceptable
        client_dataframe = pd.DataFrame([infos_clients])

        # Prediction
        prediction = self.modele_ai.predict(client_dataframe)[0] 

        # La probabilite de faire defaut (entre 0 et 1)
        # Verifier si la probabilite a pris les 2 classes 
        proba_classes = self.modele_ai.predict_proba(client_dataframe)[0]
        if len(proba_classes) == 2:
            probabilite_defaut = proba_classes[1]
        else:
            probabilite_defaut = float(prediction)
            
        return {
            'va_faire_defaut': prediction,
            'probabilite_defaut': probabilite_defaut,
            'niveau_risque': self.classifier_risque(probabilite_defaut),
            'recomandation': self.donner_recomandation(probabilite_defaut)
        }
    
    def classifier_risque(self, probabilite):
        '''Classer les niveaux de risque selon les probabilites'''
        if probabilite < 0.3:
            return 'RISQUE FAIBLE'
        elif probabilite < 0.5:
            return 'RISQUE MOYEN'
        else:
            return 'RISQUE ELEVE'
        
    def donner_recomandation(self, probabilite):
        '''Donner une recommandation selon le niveau de risque'''
        if probabilite < 0.3:
            return 'APPROUVER LE CREDIT'
        elif probabilite < 0.5:
            return 'EXAMINER LE CREDIT'
        else:
            return 'REFUSER LE CREDIT'
        
    def analyser_client(self, infos_clients):
        '''Analyse complete du client avec explication'''
        resultats = self.predire_risque_client(infos_clients)

        if resultats is None:
            return
        
        print(f"L'age : {infos_clients['age']}")
        print(f"Le revenu : {infos_clients['revenu_annuel']}")  # Corrigé: revenue_annuel -> revenu_annuel
        print(f"Le mois emploi : {infos_clients['mois_emploi']}")
        print(f"Montant : {infos_clients['montant_cherche']}")  # Corrigé: montant_recherche -> montant_cherche
        print(f"Duree remboursement : {infos_clients['duree_remboursement']}")  # Corrigé: duree_remboursemnt -> duree_remboursement
        print(f"Credit en cours : {infos_clients['nombre_credit_en_cours']}")
        print(f"score_credit : {infos_clients['score_credit']}")
        print('\n--- RESULTATS DE L\'ANALYSE ---')
        print(f"Niveau de risque : {resultats['niveau_risque']}")
        print(f"Probabilite de defaut : {resultats['probabilite_defaut']:.2%}")  # Corrigé: probabilite_deafut -> probabilite_defaut
        print(f"Recommandation : {resultats['recomandation']}")
        
        return resultats
    
    @staticmethod  # Ajouté le décorateur manquant
    def exemple_utilisation():
        # Creer un modele
        mon_modele = ModelCreditRisk()

        # Creer des donnees des clients
        donne_exemple = mon_modele.Creer_donnees_clients(n_clients=200)

        # Entrainer le modele
        precision = mon_modele.Entrainer_modele(donne_exemple)

        # Client avec un bon profil - Fleury Niyokwizera
        client_bon_profil = {
            'age': 35,
            'revenu_annuel': 5500000,  # 5.5M BIF/an
            'mois_emploi': 36,  # Corrigé: 8 -> 36 (pour éviter le risque)
            'montant_cherche': 2500000,  # 2.5M BIF
            'duree_remboursement': 36,
            'nombre_credit_en_cours': 2,
            'score_credit': 720
        }
        
        # Client avec un profil risqué - Bucumi Jean
        client_profil_risque = {
            'age': 28,
            'revenu_annuel': 2800000,  # 2.8M BIF/an
            'mois_emploi': 6,  # Corrigé: 1 -> 6
            'montant_cherche': 4500000,  # 4.5M BIF
            'duree_remboursement': 60,  # Corrigé: 72 n'existe pas dans les choix possibles
            'nombre_credit_en_cours': 4,  # Corrigé: 5 -> 4
            'score_credit': 400  # Corrigé: 580 -> 400 (plus risqué)
        }

        # Analyser les deux clients
        print("\n👤 ANALYSE CLIENT 1 - Fleury Niyokwizera (Bon profil) :")
        mon_modele.analyser_client(client_bon_profil)
        
        print("\n👤 ANALYSE CLIENT 2 - Bucumi Jean (Profil risqué) :")
        mon_modele.analyser_client(client_profil_risque)
        
        return mon_modele


if __name__ == "__main__":
    # Lancer l'exemple d'utilisation (analyse de deux clients)
    ModelCreditRisk.exemple_utilisation()