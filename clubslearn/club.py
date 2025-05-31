import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.pipeline import Pipeline
import joblib
import warnings
warnings.filterwarnings('ignore')

class CreditRiskModel:
    """
    Modèle d'IA pour prédire le risque de crédit bancaire
    
    Ce modèle utilise plusieurs algorithmes de machine learning pour évaluer
    la probabilité qu'un client rembourse son crédit ou fasse défaut.
    """
    
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.is_trained = False
        
    def generate_sample_data(self, n_samples=5000):
        """
        Génère des données d'exemple pour l'entraînement du modèle
        
        Args:
            n_samples: Nombre d'échantillons à générer
            
        Returns:
            DataFrame avec les données synthétiques
        """
        np.random.seed(42)
        
        # Génération des caractéristiques du client
        data = {
            'age': np.random.normal(40, 12, n_samples).astype(int),
            'annual_income': np.random.lognormal(10.5, 0.8, n_samples),
            'employment_years': np.random.exponential(5, n_samples),
            'loan_amount': np.random.lognormal(9.5, 1.2, n_samples),
            'loan_duration_months': np.random.choice([12, 24, 36, 48, 60, 72], n_samples),
            'credit_score': np.random.normal(650, 100, n_samples).astype(int),
            'num_credit_cards': np.random.poisson(2.5, n_samples),
            'num_previous_loans': np.random.poisson(1.8, n_samples),
            'debt_to_income_ratio': np.random.beta(2, 5, n_samples),
            'education_level': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_samples),
            'employment_status': np.random.choice(['Employed', 'Self-Employed', 'Unemployed'], n_samples, p=[0.7, 0.25, 0.05]),
            'marital_status': np.random.choice(['Single', 'Married', 'Divorced'], n_samples, p=[0.4, 0.5, 0.1]),
            'home_ownership': np.random.choice(['Own', 'Rent', 'Mortgage'], n_samples, p=[0.3, 0.4, 0.3]),
            'loan_purpose': np.random.choice(['Personal', 'Auto', 'Home', 'Business', 'Education'], n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Nettoyage des données
        df['age'] = np.clip(df['age'], 18, 80)
        df['credit_score'] = np.clip(df['credit_score'], 300, 850)
        df['employment_years'] = np.clip(df['employment_years'], 0, 40)
        df['debt_to_income_ratio'] = np.clip(df['debt_to_income_ratio'], 0, 1)
        
        # Création de la variable cible basée sur des règles logiques
        risk_score = (
            (df['credit_score'] < 600) * 0.4 +
            (df['debt_to_income_ratio'] > 0.4) * 0.3 +
            (df['employment_status'] == 'Unemployed') * 0.5 +
            (df['annual_income'] < 30000) * 0.2 +
            (df['num_previous_loans'] > 3) * 0.2 +
            np.random.normal(0, 0.1, n_samples)
        )
        
        # 1 = Défaut de paiement, 0 = Remboursement normal
        df['default'] = (risk_score > 0.6).astype(int)
        
        return df
    
    def preprocess_data(self, df, fit_encoders=True):
        """
        Prétraitement des données : encodage et normalisation
        
        Args:
            df: DataFrame à prétraiter
            fit_encoders: Si True, ajuste les encodeurs sur les données
            
        Returns:
            DataFrame prétraité
        """
        df_processed = df.copy()
        
        # Suppression des colonnes non nécessaires pour le modèle
        if 'client_id' in df_processed.columns:
            df_processed = df_processed.drop('client_id', axis=1)
        
        # Encodage des variables catégorielles
        categorical_columns = ['education_level', 'employment_status', 'marital_status', 
                             'home_ownership', 'loan_purpose']
        
        for col in categorical_columns:
            if col in df_processed.columns:
                if fit_encoders:
                    if col not in self.label_encoders:
                        self.label_encoders[col] = LabelEncoder()
                    df_processed[col] = self.label_encoders[col].fit_transform(df_processed[col])
                else:
                    if col in self.label_encoders:
                        # Gérer les valeurs inconnues
                        unique_values = set(df_processed[col].unique())
                        known_values = set(self.label_encoders[col].classes_)
                        unknown_values = unique_values - known_values
                        
                        if unknown_values:
                            # Remplacer les valeurs inconnues par la plus fréquente
                            most_frequent = self.label_encoders[col].classes_[0]
                            df_processed[col] = df_processed[col].replace(list(unknown_values), most_frequent)
                        
                        df_processed[col] = self.label_encoders[col].transform(df_processed[col])
        
        # Création de nouvelles caractéristiques
        df_processed['loan_to_income_ratio'] = df_processed['loan_amount'] / df_processed['annual_income']
        df_processed['monthly_payment_ratio'] = (df_processed['loan_amount'] / df_processed['loan_duration_months']) / (df_processed['annual_income'] / 12)
        df_processed['age_group'] = pd.cut(df_processed['age'], bins=[0, 30, 45, 60, 100], labels=[0, 1, 2, 3])
        
        return df_processed
    
    def train_models(self, X_train, y_train):
        """
        Entraîne plusieurs modèles de machine learning
        
        Args:
            X_train: Caractéristiques d'entraînement
            y_train: Variable cible d'entraînement
        """
        print("🔄 Entraînement des modèles en cours...")
        
        # Définition des modèles
        models_config = {
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(random_state=42),
            'SVM': SVC(probability=True, random_state=42)
        }
        
        # Entraînement et évaluation par validation croisée
        results = {}
        for name, model in models_config.items():
            print(f"   Entraînement: {name}")
            
            # Validation croisée
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='roc_auc')
            
            # Entraînement final
            model.fit(X_train, y_train)
            
            self.models[name] = model
            results[name] = {
                'model': model,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }
            
            print(f"   AUC moyen: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        
        # Sélection du meilleur modèle
        best_model_name = max(results.keys(), key=lambda x: results[x]['cv_mean'])
        self.best_model = self.models[best_model_name]
        
        print(f"\n✅ Meilleur modèle: {best_model_name}")
        print(f"   Score AUC: {results[best_model_name]['cv_mean']:.4f}")
        
        return results
    
    def optimize_best_model(self, X_train, y_train):
        """
        Optimise les hyperparamètres du meilleur modèle
        """
        print("\n🔧 Optimisation des hyperparamètres...")
        
        if isinstance(self.best_model, RandomForestClassifier):
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10]
            }
        elif isinstance(self.best_model, GradientBoostingClassifier):
            param_grid = {
                'n_estimators': [100, 200],
                'learning_rate': [0.05, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            }
        else:
            print("Optimisation non implémentée pour ce modèle")
            return
        
        grid_search = GridSearchCV(
            self.best_model, param_grid, cv=3, 
            scoring='roc_auc', n_jobs=-1, verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        self.best_model = grid_search.best_estimator_
        
        print(f"✅ Meilleurs paramètres: {grid_search.best_params_}")
        print(f"   Score AUC optimisé: {grid_search.best_score_:.4f}")
    
    def fit(self, df, optimize=True):
        """
        Entraîne le modèle complet sur les données
        
        Args:
            df: DataFrame avec les données d'entraînement
            optimize: Si True, optimise les hyperparamètres
        """
        print("🚀 Début de l'entraînement du modèle de risque de crédit")
        
        # Prétraitement
        df_processed = self.preprocess_data(df, fit_encoders=True)
        
        # Séparation des caractéristiques et de la cible
        X = df_processed.drop(['default'], axis=1)
        y = df_processed['default']
        
        self.feature_names = X.columns.tolist()
        
        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Normalisation
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entraînement des modèles
        results = self.train_models(X_train_scaled, y_train)
        
        # Optimisation
        if optimize:
            self.optimize_best_model(X_train_scaled, y_train)
        
        # Évaluation finale
        self.evaluate_model(X_test_scaled, y_test)
        
        self.is_trained = True
        print("\n🎉 Entraînement terminé avec succès!")
        
        return results
    
    def predict_proba(self, X):
        """
        Prédit la probabilité de défaut
        
        Args:
            X: Caractéristiques du client
            
        Returns:
            Probabilité de défaut (0-1)
        """
        if not self.is_trained:
            raise ValueError("Le modèle n'est pas encore entraîné!")
        
        if isinstance(X, pd.DataFrame):
            X_processed = self.preprocess_data(X, fit_encoders=False)
            X_scaled = self.scaler.transform(X_processed)
        else:
            X_scaled = self.scaler.transform(X.reshape(1, -1))
        
        return self.best_model.predict_proba(X_scaled)[:, 1]
    
    def predict(self, X, threshold=0.5):
        """
        Prédit la classe de risque
        
        Args:
            X: Caractéristiques du client
            threshold: Seuil de décision
            
        Returns:
            Prédiction binaire (0/1)
        """
        probas = self.predict_proba(X)
        return (probas >= threshold).astype(int)
    
    def evaluate_model(self, X_test, y_test):
        """
        Évalue les performances du modèle
        """
        print("\n📊 Évaluation du modèle:")
        
        # Prédictions
        y_pred = self.best_model.predict(X_test)
        y_pred_proba = self.best_model.predict_proba(X_test)[:, 1]
        
        # Métriques
        auc_score = roc_auc_score(y_test, y_pred_proba)
        print(f"AUC Score: {auc_score:.4f}")
        
        print("\nRapport de classification:")
        print(classification_report(y_test, y_pred))
        
        # Matrice de confusion
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nMatrice de confusion:")
        print(f"[[TN: {cm[0,0]}, FP: {cm[0,1]}]")
        print(f" [FN: {cm[1,0]}, TP: {cm[1,1]}]]")
        
        return auc_score
    
    def get_feature_importance(self, top_n=10):
        """
        Retourne l'importance des caractéristiques
        """
        if hasattr(self.best_model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.best_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return importance_df.head(top_n)
        else:
            print("Ce modèle ne fournit pas d'importance des caractéristiques")
            return None
    
    def plot_roc_curve(self, X_test, y_test):
        """
        Affiche la courbe ROC
        """
        y_pred_proba = self.best_model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        auc_score = roc_auc_score(y_test, y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc_score:.4f})')
        plt.plot([0, 1], [0, 1], 'k--', label='Random')
        plt.xlabel('Taux de Faux Positifs')
        plt.ylabel('Taux de Vrais Positifs')
        plt.title('Courbe ROC - Modèle de Risque de Crédit')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def assess_client_risk(self, client_data):
        """
        Évalue le risque d'un client spécifique avec explications détaillées
        
        Args:
            client_data: Dictionnaire avec les données du client
            
        Returns:
            Dictionnaire avec l'évaluation complète
        """
        if not self.is_trained:
            raise ValueError("Le modèle n'est pas encore entraîné!")
        
        # Copie des données sans client_id pour éviter les erreurs
        client_data_clean = {k: v for k, v in client_data.items() if k != 'client_id'}
        
        # Conversion en DataFrame
        client_df = pd.DataFrame([client_data_clean])
        
        # Prédiction
        risk_probability = self.predict_proba(client_df)[0]
        risk_class = self.predict(client_df)[0]
        
        # Classification du risque
        if risk_probability < 0.3:
            risk_level = "FAIBLE"
            recommendation = "APPROUVER - Client à faible risque"
            color = "🟢"
        elif risk_probability < 0.6:
            risk_level = "MODÉRÉ"
            recommendation = "EXAMINER - Analyse supplémentaire recommandée"
            color = "🟡"
        else:
            risk_level = "ÉLEVÉ"
            recommendation = "REJETER - Risque trop élevé"
            color = "🔴"
        
        # Analyse des facteurs de risque
        risk_factors = []
        if client_data_clean.get('credit_score', 700) < 600:
            risk_factors.append("Score de crédit faible")
        if client_data_clean.get('debt_to_income_ratio', 0.2) > 0.4:
            risk_factors.append("Ratio dette/revenu élevé")
        if client_data_clean.get('employment_status') == 'Unemployed':
            risk_factors.append("Statut d'emploi: Chômeur")
        if client_data_clean.get('annual_income', 50000) < 30000:
            risk_factors.append("Revenu annuel faible")
        
        return {
            'client_id': client_data.get('client_id', 'N/A'),
            'risk_probability': risk_probability,
            'risk_class': risk_class,
            'risk_level': risk_level,
            'recommendation': recommendation,
            'risk_factors': risk_factors,
            'color': color,
            'confidence': max(risk_probability, 1 - risk_probability)
        }
    
    def save_model(self, filepath):
        """Sauvegarde le modèle"""
        joblib.dump({
            'best_model': self.best_model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }, filepath)
        print(f"✅ Modèle sauvegardé: {filepath}")
    
    def load_model(self, filepath):
        """Charge un modèle sauvegardé"""
        data = joblib.load(filepath)
        self.best_model = data['best_model']
        self.scaler = data['scaler']
        self.label_encoders = data['label_encoders']
        self.feature_names = data['feature_names']
        self.is_trained = data['is_trained']
        print(f"✅ Modèle chargé: {filepath}")


# ========================================
# EXEMPLES D'UTILISATION PRATIQUES
# ========================================

def demo_credit_risk_model():
    """
    Démonstration complète du modèle de risque de crédit
    """
    print("=" * 60)
    print("🏦 DÉMONSTRATION - MODÈLE IA DE RISQUE DE CRÉDIT BANCAIRE")
    print("=" * 60)
    
    # 1. Initialisation du modèle
    print("\n1️⃣ Initialisation du modèle")
    credit_model = CreditRiskModel()
    
    # 2. Génération des données d'exemple
    print("\n2️⃣ Génération des données d'entraînement")
    sample_data = credit_model.generate_sample_data(n_samples=3000)
    print(f"   Données générées: {len(sample_data)} échantillons")
    print(f"   Taux de défaut: {sample_data['default'].mean():.2%}")
    
    # 3. Entraînement du modèle
    print("\n3️⃣ Entraînement du modèle")
    results = credit_model.fit(sample_data, optimize=True)
    
    # 4. Analyse de l'importance des caractéristiques
    print("\n4️⃣ Importance des caractéristiques")
    importance = credit_model.get_feature_importance()
    if importance is not None:
        print(importance.to_string(index=False))
    
    # 5. Tests sur des clients fictifs
    print("\n5️⃣ Évaluation de clients fictifs")
    
    # Client à faible risque
    client_low_risk = {
        'age': 35,
        'annual_income': 75000,
        'employment_years': 8,
        'loan_amount': 25000,
        'loan_duration_months': 36,
        'credit_score': 750,
        'num_credit_cards': 2,
        'num_previous_loans': 1,
        'debt_to_income_ratio': 0.25,
        'education_level': 'Bachelor',
        'employment_status': 'Employed',
        'marital_status': 'Married',
        'home_ownership': 'Own',
        'loan_purpose': 'Auto'
    }
    
    # Client à risque élevé
    client_high_risk = {
        'age': 28,
        'annual_income': 28000,
        'employment_years': 1,
        'loan_amount': 40000,
        'loan_duration_months': 72,
        'credit_score': 520,
        'num_credit_cards': 5,
        'num_previous_loans': 4,
        'debt_to_income_ratio': 0.65,
        'education_level': 'High School',
        'employment_status': 'Self-Employed',
        'marital_status': 'Single',
        'home_ownership': 'Rent',
        'loan_purpose': 'Personal'
    }
    
    # Évaluations
    print("\n📋 CLIENT 1 - Profil Favorable:")
    evaluation1 = credit_model.assess_client_risk(client_low_risk)
    print(f"{evaluation1['color']} Probabilité de défaut: {evaluation1['risk_probability']:.1%}")
    print(f"   Niveau de risque: {evaluation1['risk_level']}")
    print(f"   Recommandation: {evaluation1['recommendation']}")
    if evaluation1['risk_factors']:
        print(f"   Facteurs de risque: {', '.join(evaluation1['risk_factors'])}")
    
    print("\n📋 CLIENT 2 - Profil Risqué:")
    evaluation2 = credit_model.assess_client_risk(client_high_risk)
    print(f"{evaluation2['color']} Probabilité de défaut: {evaluation2['risk_probability']:.1%}")
    print(f"   Niveau de risque: {evaluation2['risk_level']}")
    print(f"   Recommandation: {evaluation2['recommendation']}")
    if evaluation2['risk_factors']:
        print(f"   Facteurs de risque: {', '.join(evaluation2['risk_factors'])}")
    
    # 6. Sauvegarde du modèle
    print("\n6️⃣ Sauvegarde du modèle")
    credit_model.save_model("credit_risk_model.pkl")
    
    return credit_model


def batch_risk_assessment(credit_model, clients_data):
    """
    Évaluation en lot de plusieurs clients
    
    Args:
        credit_model: Modèle entraîné
        clients_data: Liste de dictionnaires avec les données clients
    
    Returns:
        DataFrame avec les résultats d'évaluation
    """
    results = []
    
    for i, client in enumerate(clients_data):
        client['client_id'] = f"CLIENT_{i+1:03d}"
        evaluation = credit_model.assess_client_risk(client)
        
        results.append({
            'Client_ID': evaluation['client_id'],
            'Probabilité_Défaut': f"{evaluation['risk_probability']:.1%}",
            'Niveau_Risque': evaluation['risk_level'],
            'Recommandation': evaluation['recommendation'],
            'Facteurs_Risque': len(evaluation['risk_factors']),
            'Confiance': f"{evaluation['confidence']:.1%}"
        })
    
    return pd.DataFrame(results)


# ========================================
# INTERFACE INTERACTIVE POUR TESTS
# ========================================

def interactive_client_assessment():
    """
    Interface interactive pour tester le modèle avec des données personnalisées
    """
    print("\n🔍 ÉVALUATEUR INTERACTIF DE RISQUE DE CRÉDIT")
    print("-" * 50)
    
    # Chargement ou création du modèle
    try:
        credit_model = CreditRiskModel()
        credit_model.load_model("credit_risk_model.pkl")
        print("✅ Modèle pré-entraîné chargé")
    except:
        print("⚠️  Modèle non trouvé, entraînement en cours...")
        credit_model = demo_credit_risk_model()
    
    # Saisie des données client
    print("\n📝 Veuillez saisir les informations du client:")
    
    client_data = {
        'age': int(input("Âge: ") or 35),
        'annual_income': float(input("Revenu annuel (€): ") or 50000),
        'employment_years': float(input("Années d'emploi: ") or 5),
        'loan_amount': float(input("Montant du prêt (€): ") or 30000),
        'loan_duration_months': int(input("Durée du prêt (mois): ") or 36),
        'credit_score': int(input("Score de crédit (300-850): ") or 650),
        'num_credit_cards': int(input("Nombre de cartes de crédit: ") or 2),
        'num_previous_loans': int(input("Nombre de prêts antérieurs: ") or 1),
        'debt_to_income_ratio': float(input("Ratio dette/revenu (0-1): ") or 0.3),
        'education_level': input("Niveau d'éducation (High School/Bachelor/Master/PhD): ") or 'Bachelor',
        'employment_status': input("Statut d'emploi (Employed/Self-Employed/Unemployed): ") or 'Employed',
        'marital_status': input("Statut marital (Single/Married/Divorced): ") or 'Single',
        'home_ownership': input("Propriété (Own/Rent/Mortgage): ") or 'Rent',
        'loan_purpose': input("Objectif du prêt (Personal/Auto/Home/Business/Education): ") or 'Personal'
    }
    
    # Évaluation
    evaluation = credit_model.assess_client_risk(client_data)
    
    # Affichage des résultats
    print("\n" + "="*60)
    print("📊 RÉSULTAT DE L'ÉVALUATION")
    print("="*60)
    print(f"{evaluation['color']} PROBABILITÉ DE DÉFAUT: {evaluation['risk_probability']:.1%}")
    print(f"📈 NIVEAU DE RISQUE: {evaluation['risk_level']}")
    print(f"💼 RECOMMANDATION: {evaluation['recommendation']}")
    print(f"🎯 CONFIANCE: {evaluation['confidence']:.1%}")
    
    if evaluation['risk_factors']:
        print(f"\n⚠️  FACTEURS DE RISQUE IDENTIFIÉS:")
        for factor in evaluation['risk_factors']:
            print(f"   • {factor}")
    else:
        print(f"\n✅ Aucun facteur de risque majeur identifié")


# ========================================
# EXÉCUTION DE LA DÉMONSTRATION
# ========================================

if __name__ == "__main__":
    # Démonstration complète
    trained_model = demo_credit_risk_model()
    
    # Test avec plusieurs clients
    print("\n" + "="*60)
    print("📊 ÉVALUATION EN LOT DE PLUSIEURS CLIENTS")
    print("="*60)
    
    # Extension avec 5 clients de test
    test_clients = [
        # Client excellent
        {'age': 42, 'annual_income': 85000, 'employment_years': 12, 'loan_amount': 30000, 
         'loan_duration_months': 36, 'credit_score': 780, 'num_credit_cards': 3, 
         'num_previous_loans': 2, 'debt_to_income_ratio': 0.2, 'education_level': 'Master',
         'employment_status': 'Employed', 'marital_status': 'Married', 'home_ownership': 'Own',
         'loan_purpose': 'Home'},
        
        # Client moyen
        {'age': 30, 'annual_income': 45000, 'employment_years': 5, 'loan_amount': 20000,
         'loan_duration_months': 48, 'credit_score': 650, 'num_credit_cards': 2,
         'num_previous_loans': 1, 'debt_to_income_ratio': 0.35, 'education_level': 'Bachelor',
         'employment_status': 'Employed', 'marital_status': 'Single', 'home_ownership': 'Rent',
         'loan_purpose': 'Auto'},
        
        # Client risqué
        {'age': 25, 'annual_income': 25000, 'employment_years': 1, 'loan_amount': 35000,
         'loan_duration_months': 72, 'credit_score': 580, 'num_credit_cards': 4,
         'num_previous_loans': 3, 'debt_to_income_ratio': 0.55, 'education_level': 'High School',
         'employment_status': 'Self-Employed', 'marital_status': 'Single', 'home_ownership': 'Rent',
         'loan_purpose': 'Personal'}
    ]
    
    batch_results = batch_risk_assessment(trained_model, test_clients)
    print(batch_results.to_string(index=False))
    
    print("\n🎉 Démonstration terminée!")
    print("💡 Utilisez interactive_client_assessment() pour tester vos propres données")