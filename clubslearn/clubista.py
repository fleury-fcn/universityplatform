import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

class ModelRiskCredit:

    def __init__(self):
        self.modele_ai = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained= False
    
    def Generer_donnees_client(self, n_clients = 1000):

        print(f'Bases des donnes de {n_clients}')
        np.random.seed(42)

        donnes_clients = {
            # Information perosonnelle
            'age': np.random.randint(18, 80, n_clients),
            'revenu_annuel': np.random.randint(2000000, 15000000, n_clients),
            'Annees_Emploi': np.random.randint(0, 40, n_clients),

            #Information du credit
            'Montant_recheche': np.random.randint(5000000, 20000000, n_clients),
            'Duree_rembouresement': np.random.choice([12, 24, 36, 48, 60, 72], n_clients),

            # Historique credit
            'Credit_en_cours': np.random.randint(0, 5, n_clients),
            'score_credit': np.random.randint(300, 850, n_clients),

        }

        # Convertir en Tableau
        clients_df = pd.DataFrame(donnes_clients)
        

        ''' Si deux conditions sont remplis ici, le client presente un risque de defaut''' 
        conditions_risque = (
            (clients_df['revenu_annuel'] < 300000 ) + # revenu faible
            (clients_df['Annees_Emploi'] < 10 ) +  # Anciennette faible
            (clients_df['Montant_recheche'] > 1500000 ) + # Montant eleve
            (clients_df['Credit_en_cours'] >= 3 ) + # Exces de credit en cours
            (clients_df['score_credit'] < 500 ) 

        )

        clients_df['Risque_client'] = (conditions_risque >= 2).astype(int)

        pourcentage_risque = clients_df['Risque_client'].mean() * 100
        print(f'Le pourcentage des risques est : {pourcentage_risque:.2f}%')
        print(clients_df.head(20))

        return clients_df
    

    def entrainer_model(self, clients_df):

        # Detemination de X features et Y target
        features= clients_df.drop('Risque_client',  axis = 1)
        target = clients_df['Risque_client']

        # Division d'entrainement est de test, 80% pour entrainement et 20% pour test
        x_train, x_test, y_train, y_test = train_test_split(
            features,
            target,
            test_size= 0.2,
            random_state=42
        )
        # Entrainer le modele
        self.modele_ai.fit(x_train, y_train)
        
        # prediction du modele et precision
        predictions_test = self.modele_ai.predict(x_test)
        precisions_test = accuracy_score(y_test, predictions_test)
        
        self.is_trained = True

        print(f"Le Precision est {precisions_test:.1%}")
        return precisions_test


if __name__ == '__main__':
    mon_modele = ModelRiskCredit()

    df = mon_modele.Generer_donnees_client()
    pr = mon_modele.entrainer_model(df)
    print(pr)
    


