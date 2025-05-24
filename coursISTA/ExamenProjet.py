import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Importation des données à partir du fichier CSV
data = pd.read_csv('~/projets/OpenISTA/coursISTA/data.csv')

# Affichage des premières lignes du DataFrame
print("Aperçu des 25 premières lignes du DataFrame (data.head(25)):")
#print(data.head(25))

# Affichage des statistiques descriptives du DataFrame
print("\nStatistiques descriptives du DataFrame (data.describe()):\n\n")
#print(data.describe())


# Création du tableau croisé Genre vs. Jeux
tableau_genre_jeux = pd.crosstab(data['Genre'], data['Jeux'])
print(tableau_genre_jeux)

# Catégorisation des résultats
bins = [0, 10, 15, 20]
labels = ['Faibles', 'Moyens', 'Elevés']
data['Resultats_Categories'] = pd.cut(data['Resultats'], bins=bins, labels=labels, right=False)

# Création du tableau croisé Genre vs. Catégories de Résultats
tableau_genre_resultats = pd.crosstab(data['Genre'], data['Resultats_Categories'])
print(tableau_genre_resultats)



# Calcul de la moyenne du revenu par genre
moyenne_revenu_par_genre = data.groupby('Genre')['Revenu'].mean()
print("Moyenne du revenu par genre:")
print(moyenne_revenu_par_genre)

# Calcul de la médiane du revenu par genre
mediane_revenu_par_genre = data.groupby('Genre')['Revenu'].median()
print("\nMédiane du revenu par genre:")
print(mediane_revenu_par_genre)


# Calcul de l'écart type du revenu par genre
ecart_type_revenu_par_genre = data.groupby('Genre')['Revenu'].std()
print("Écart type du revenu par genre:")
print(ecart_type_revenu_par_genre)

# Calcul de la variance du revenu par genre
variance_revenu_par_genre = data.groupby('Genre')['Revenu'].var()
print("\nVariance du revenu par genre:")
print(variance_revenu_par_genre)


# Création d'une boîte à moustaches du revenu par genre
data.boxplot(column='Revenu', by='Genre')
plt.title('Distribution du Revenu par Genre')
plt.suptitle('')  # Supprime le sous-titre automatique
plt.ylabel('Revenu')
plt.show()




# Affichage des types de données de chaque colonne
print("Types de données des colonnes:\n", data.dtypes)

# Identification des colonnes numériques
numeric_columns = data.select_dtypes(include=['number']).columns

# Calcul de la corrélation de Pearson entre 'Resultats' et 'Revenu' (si elles sont numériques)
if 'Resultats' in numeric_columns and 'Revenu' in numeric_columns:
    correlation_pearson = data['Resultats'].corr(data['Revenu'], method='pearson')
    print("Corrélation de Pearson entre Résultats et Revenu:", correlation_pearson)
else:
    print("Les colonnes 'Resultats' ou 'Revenu' ne sont pas numériques.")

# Calcul de la matrice de corrélation de Pearson pour toutes les variables numériques
matrice_correlation_pearson = data[numeric_columns].corr(method='pearson')
print("\nMatrice de corrélation de Pearson:")
print(matrice_correlation_pearson)



# Affichage des types de données de chaque colonne
print("Types de données des colonnes:\n", data.dtypes)

# Identification des colonnes numériques
numeric_columns = data.select_dtypes(include=['number']).columns

# Calcul de la corrélation de Spearman entre 'Resultats' et 'Revenu' (si elles sont numériques)
if 'Resultats' in numeric_columns and 'Revenu' in numeric_columns:
    correlation_spearman = data['Resultats'].corr(data['Revenu'], method='spearman')
    print("Corrélation de Spearman entre Résultats et Revenu:", correlation_spearman)
else:
    print("Les colonnes 'Resultats' ou 'Revenu' ne sont pas numériques.")

# Calcul de la matrice de corrélation de Spearman pour toutes les variables numériques
matrice_correlation_spearman = data[numeric_columns].corr(method='spearman')
print("\nMatrice de corrélation de Spearman:")
print(matrice_correlation_spearman)


# Affichage des types de données de chaque colonne
print("Types de données des colonnes:\n", data.dtypes)

# Identification des colonnes numériques
numeric_columns = data.select_dtypes(include=['number']).columns

# Vérification que les colonnes 'Resultats' et 'Revenu' sont numériques
if 'Resultats' in numeric_columns and 'Revenu' in numeric_columns:
    # Création d'un nuage de points entre 'Resultats' et 'Revenu'
    data.plot.scatter(x='Resultats', y='Revenu')
    plt.title('Nuage de Points: Résultats vs. Revenu')
    plt.xlabel('Résultats')
    plt.ylabel('Revenu')
    plt.show()
else:
    print("Les colonnes 'Resultats' ou 'Revenu' ne sont pas numériques. Veuillez vérifier les types de données.")





# Identification des colonnes numériques
numeric_columns = data.select_dtypes(include=['number']).columns

# Calcul de la matrice de corrélation (Pearson) pour les colonnes numériques
matrice_correlation = data[numeric_columns].corr(method='pearson')

# Création de la heatmap
plt.figure(figsize=(10, 8))  # Ajuster la taille de la figure
sns.heatmap(matrice_correlation, annot=True, cmap='coolwarm', linewidths=.5)
plt.title('Heatmap de la Matrice de Corrélation (Pearson)')
plt.show()



from scipy.stats import chi2_contingency
# Vérification des colonnes et gestion des valeurs manquantes
if 'Genre' not in data.columns or 'Jeux' not in data.columns:
    print("Erreur: Les colonnes 'Genre' ou 'Jeux' sont manquantes dans le DataFrame.")
else:
    # Suppression des lignes avec des valeurs manquantes dans les colonnes 'Genre' et 'Jeux'
    data_cleaned = data.dropna(subset=['Genre', 'Jeux'])

    # Vérification que les colonnes 'Genre' et 'Jeux' contiennent des données catégorielles
    if data_cleaned['Genre'].dtype == 'object' and data_cleaned['Jeux'].dtype == 'object':

        # Création d'un tableau croisé
        tableau_croise = pd.crosstab(data_cleaned['Genre'], data_cleaned['Jeux'])

        # Exécution du test du Chi-Deux
        chi2, p, dof, expected = chi2_contingency(tableau_croise)
        print("Statistique Chi-Deux:", chi2)
        print("P-valeur:", p)
        print("Degrés de liberté:", dof)
        print("Tableau des valeurs attendues:\n", expected)
    else:
        print("Erreur: Les colonnes 'Genre' et 'Jeux' doivent être de type catégoriel (object).")




from scipy.stats import ttest_ind
# Vérification des colonnes et gestion des valeurs manquantes
if 'Genre' not in data.columns or 'Revenu' not in data.columns:
    print("Erreur: Les colonnes 'Genre' ou 'Revenu' sont manquantes dans le DataFrame.")
else:
    # Suppression des lignes avec des valeurs manquantes dans les colonnes 'Genre' et 'Revenu'
    data_cleaned = data.dropna(subset=['Genre', 'Revenu'])

    # Vérification que la colonne 'Revenu' est de type numérique
    if data_cleaned['Revenu'].dtype in ['int64', 'float64']:

        # Séparation des données en deux groupes (par exemple, Genre == 'Homme' et Genre == 'Femme')
        groupe_homme = data_cleaned[data_cleaned['Genre'] == 'M']['Revenu']
        groupe_femme = data_cleaned[data_cleaned['Genre'] == 'F']['Revenu']

        # Gestion du cas où l'un des groupes est vide
        if groupe_homme.empty or groupe_femme.empty:
            print("Avertissement: L'un des groupes (Homme ou Femme) est vide. Impossible d'effectuer le test t.")
        else:
            # Exécution du test t indépendant
            t_statistic, p_value = ttest_ind(groupe_homme, groupe_femme)

            print("Statistique t:", t_statistic)
            print("P-valeur:", p_value)
    else:
        print("Erreur: La colonne 'Revenu' doit être de type numérique.")



from scipy.stats import f_oneway

# Suppression des lignes avec des valeurs manquantes dans les colonnes 'Jeux' et 'Revenu'
data_cleaned = data.dropna(subset=['Jeux', 'Revenu'])

# Vérification que la colonne 'Revenu' est de type numérique
if data_cleaned['Revenu'].dtype not in ['int64', 'float64']:
    print("Erreur: La colonne 'Revenu' doit être de type numérique.")
else:
    # Récupération des valeurs uniques de la colonne 'Jeux'
    jeux_uniques = data_cleaned['Jeux'].unique()

    # Création des groupes
    groupes = []
    for jeu in jeux_uniques:
        groupe = data_cleaned[data_cleaned['Jeux'] == jeu]['Revenu']
        # Vérification que le groupe n'est pas vide
        if not groupe.empty:
            groupes.append(groupe)
        else:
            print(f"Avertissement: Le groupe pour le jeu '{jeu}' est vide. Il sera ignoré dans l'ANOVA.")

    # Vérification qu'il y a au moins deux groupes non vides pour effectuer l'ANOVA
    if len(groupes) < 2:
        print("Erreur: Il doit y avoir au moins deux groupes non vides pour effectuer l'ANOVA.")
    else:
        # Exécution de l'ANOVA
        f_statistic, p_value = f_oneway(*groupes)

        print("Statistique F:", f_statistic)
        print("P-valeur:", p_value)

        

# 2. Préparer les données
X = data['Revenu']  # Variable indépendante (Revenu)
y = data['Resultats']  # Variable dépendante (Resultats)

# 3. Calculer les moyennes
mean_x = np.mean(X)
mean_y = np.mean(y)

# 4. Calculer les sommes des carrés et des produits croisés
SS_xy = np.sum(y * X) - len(X) * mean_y * mean_x
SS_xx = np.sum(X * X) - len(X) * mean_x * mean_x

# 5. Calculer les coefficients
b1 = SS_xy / SS_xx  # Pente (coefficient de la variable indépendante)
b0 = mean_y - b1 * mean_x  # Intercept (constante)

# 6. Afficher les coefficients
print("Intercept (b0):", b0)
print("Coefficient (b1):", b1)

# 7. Faire des prédictions (facultatif)
# Exemple : Prédire le résultat pour un revenu de 300000
revenu_a_predire = 300000
resultat_predit = b0 + b1 * revenu_a_predire
print(f"Résultat prédit pour un revenu de {revenu_a_predire}: {resultat_predit}")

# 8. Tracer la ligne de régression (facultatif)
plt.scatter(X, y, color='gray')
plt.plot(X, b0 + b1 * X, color='red')
plt.xlabel('Revenu')
plt.ylabel('Resultats')
plt.title('Linear Regression (Sans Scikit-learn)')
plt.show()

# 9. Calculer R-squared (facultatif)
y_predicted = b0 + b1 * X
SS_res = np.sum((y - y_predicted) ** 2)
SS_tot = np.sum((y - mean_y) ** 2)
r_squared = 1 - (SS_res / SS_tot)
print("R-squared:", r_squared)


import pandas as pd
import numpy as np
import io
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

# 1. Charger les données (directement depuis la chaîne de caractères)
data_string = """
Nom,Resultats,Revenu,Jeux,Genre,Classe
Fleury,20,200000,Football,M,1
Cherissa,12,120000,Tenis,F,0
jimy,14,15000,Rigbey,M,0
Fedor,16,47000,Course,M,0
Aline,10,12300,Tennis,F,0
Alexendre,12,562000,Natation,M,1
Prudence,8,45000,Javelon,M,0
Ange,8,123000,poids,F,0
Kenny,14,4500,Karate,M,0
Aimable,13,78000,Rudo,M,0
Nicole,12,30200,jido,F,0
jean,11,180000,Football,M,1
Alex,11,250000,Tenis,F,1
claudej,0,360000,Rigbey,M,1
Vianney,1,480000,Course,M,1
Jean de Dieu,12,450000,Tennis,F,1
Bella,15,56000,Natation,M,0
youena,18,78000,Javelon,M,0
Kayezu,10,1000000,poids,F,1
jaja,12,456000,Karate,M,1
cesar,11,45200,Rudo,M,0
tite,19,780000,jido,F,1
Orni,20,150000,Football,M,0
kiki,7,250000,Tenis,F,1
Brianne,9,500000,Rigbey,M,1
Dorine,16,780000,Course,M,1
Douce,14,98000,Tennis,F,0
Nicky,10,456000,Natation,M,1
Andre,8,789000,Javelon,M,1
"""

data = pd.read_csv(io.StringIO(data_string))

# 2. Préparer les données
X = data[['Revenu', 'Resultats']]  # Variables indépendantes
y = data['Classe']  # Variable dépendante (cible)

# 3. Diviser les données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# 4. Créer et entraîner le modèle de régression logistique
model = LogisticRegression()
model.fit(X_train, y_train)

# 5. Faire des prédictions sur l'ensemble de test
y_pred = model.predict(X_test)

# 6. Évaluer le modèle
print('Accuracy:', metrics.accuracy_score(y_test, y_pred))
print('Confusion Matrix:\n', metrics.confusion_matrix(y_test, y_pred))
print('Classification Report:\n', metrics.classification_report(y_test, y_pred))

# 7. Afficher les coefficients
print('Intercept:', model.intercept_)
print('Coefficients:', model.coef_)

# 8. Exemple de prédiction pour un nouvel individu
nouveau_revenu = 300000
nouveaux_resultats = 15
nouvel_individu = np.array([[nouveau_revenu, nouveaux_resultats]])

# Faire la prédiction
prediction = model.predict(nouvel_individu)

# Afficher la prédiction
if prediction[0] == 1:
    print("L'individu est prédit comme étant un client fidèle.")
else:
    print("L'individu est prédit comme n'étant pas un client fidèle.")

# Pour obtenir la probabilité d'appartenir à chaque classe :
proba = model.predict_proba(nouvel_individu)
print("Probabilité d'être dans la classe 0 :", proba[0][0])
print("Probabilité d'être dans la classe 1 :", proba[0][1])


# Identification des colonnes numériques
numeric_columns = data.select_dtypes(include=['number']).columns

# Calcul de la matrice de corrélation (Pearson) pour les colonnes numériques
matrice_correlation = data[numeric_columns].corr(method='pearson')

# Création de la heatmap
plt.figure(figsize=(10, 8))  # Ajuster la taille de la figure
sns.heatmap(matrice_correlation, annot=True, cmap='coolwarm', linewidths=.5)
plt.title('Heatmap de la Matrice de Corrélation (pearson)')
plt.show()


#################################################################################################

import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import LabelEncoder

# 1. Préparation des données
data = {
    'Nom': ['Fleury', 'Cherissa', 'jimy', 'Fedor', 'Aline', 'Alexendre', 'Prudence', 'Ange', 'Kenny', 'Aimable', 'Nicole', 'jean', 'Alex', 'claudej', 'Vianney', 'Jean de Dieu', 'Bella', 'youena', 'Kayezu', 'jaja', 'cesar', 'tite', 'Orni', 'kiki', 'Brianne', 'Dorine', 'Douce', 'Nicky', 'Andre'],
    'Resultats': [20, 12, 14, 16, 10, 12, 8, 8, 14, 13, 12, 11, 11, 0, 1, 12, 15, 18, 10, 12, 11, 19, 20, 7, 9, 16, 14, 10, 8],
    'Revenu': [200000, 120000, 15000, 47000, 12300, 562000, 45000, 123000, 4500, 78000, 30200, 180000, 250000, 360000, 480000, 450000, 56000, 78000, 1000000, 456000, 45200, 780000, 150000, 250000, 500000, 780000, 98000, 456000, 789000],
    'Jeux': ['Football', 'Tenis', 'Rigbey', 'Course', 'Tennis', 'Natation', 'Javelon', 'poids', 'Karate', 'Rudo', 'jido', 'Football', 'Tenis', 'Rigbey', 'Course', 'Tennis', 'Natation', 'Javelon', 'poids', 'Karate', 'Rudo', 'jido', 'Football', 'Tenis', 'Rigbey', 'Course', 'Tennis', 'Natation', 'Javelon'],
    'Genre': ['M', 'F', 'M', 'M', 'F', 'M', 'M', 'F', 'M', 'M', 'F', 'M', 'F', 'M', 'M', 'F', 'M', 'M', 'F', 'M', 'M', 'F', 'M', 'F', 'M', 'M', 'F', 'M', 'M'],
    'Classe': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1]
}

df = pd.DataFrame(data)

# 2. Nettoyage et encodage
# Encodage des variables catégorielles
le = LabelEncoder()
df['Jeux_encoded'] = le.fit_transform(df['Jeux'])
df['Genre_encoded'] = le.fit_transform(df['Genre'])

# 3. Préparation des variables
X = df[['Revenu', 'Jeux_encoded', 'Genre_encoded', 'Classe']]
y = df['Resultats']

# Ajout d'une constante (intercept)
X = sm.add_constant(X)

# 4. Régression multiple
model = sm.OLS(y, X).fit()

# 5. Affichage des résultats
print(model.summary())

# 6. Interprétation visuelle
import matplotlib.pyplot as plt

# Coefficients standardisés
coeff = model.params.drop('const')
(coeff / coeff.max()).plot.barh()
plt.title('Importance relative des variables')
plt.show()

# Essayer avec des transformations
df['log_Revenu'] = np.log(df['Revenu'] + 1)  # Éviter log(0)

# Nouvelle régression
X = df[['log_Revenu', 'Jeux_encoded', 'Genre_encoded', 'Classe']]
X = sm.add_constant(X)
model_v2 = sm.OLS(y, X).fit()
print(model_v2.summary())

###########################################################################################################

## Préparation des Données
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

# Données fournies
data = {
    'Nom': ['Fleury', 'Cherissa', 'jimy', 'Fedor', 'Aline', 'Alexendre', 'Prudence', 'Ange', 'Kenny', 'Aimable', 'Nicole', 'jean', 'Alex', 'claudej', 'Vianney', 'Jean de Dieu', 'Bella', 'youena', 'Kayezu', 'jaja', 'cesar', 'tite', 'Orni', 'kiki', 'Brianne', 'Dorine', 'Douce', 'Nicky', 'Andre'],
    'Resultats': [20, 12, 14, 16, 10, 12, 8, 8, 14, 13, 12, 11, 11, 0, 1, 12, 15, 18, 10, 12, 11, 19, 20, 7, 9, 16, 14, 10, 8],
    'Revenu': [200000, 120000, 15000, 47000, 12300, 562000, 45000, 123000, 4500, 78000, 30200, 180000, 250000, 360000, 480000, 450000, 56000, 78000, 1000000, 456000, 45200, 780000, 150000, 250000, 500000, 780000, 98000, 456000, 789000],
    'Jeux': ['Football', 'Tenis', 'Rigbey', 'Course', 'Tennis', 'Natation', 'Javelon', 'poids', 'Karate', 'Rudo', 'jido', 'Football', 'Tenis', 'Rigbey', 'Course', 'Tennis', 'Natation', 'Javelon', 'poids', 'Karate', 'Rudo', 'jido', 'Football', 'Tenis', 'Rigbey', 'Course', 'Tennis', 'Natation', 'Javelon'],
    'Genre': ['M', 'F', 'M', 'M', 'F', 'M', 'M', 'F', 'M', 'M', 'F', 'M', 'F', 'M', 'M', 'F', 'M', 'M', 'F', 'M', 'M', 'F', 'M', 'F', 'M', 'M', 'F', 'M', 'M'],
    'Classe': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1]
}

df = pd.DataFrame(data)

# Nettoyage des données
df['Jeux'] = df['Jeux'].str.lower().str.strip()

# Séparation des Features et Target
X = df[['Revenu', 'Jeux', 'Genre', 'Classe']]  # Features
y = df['Resultats']  # Target

# Prétraitement des Variables
# Transformation des variables catégorielles (Jeux, Genre) et numériques (Revenu)
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['Revenu']),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['Jeux', 'Genre', 'Classe'])
    ])

X_processed = preprocessor.fit_transform(X)

# Division en Train/Test
X_train, X_test, y_train, y_test = train_test_split(
    X_processed, y, test_size=0.2, random_state=42
)

# Entraînement du Modèle Random Forest
rf_model = RandomForestRegressor(
    n_estimators=100,  # Nombre d'arbres
    max_depth=5,       # Profondeur maximale
    random_state=42
)

rf_model.fit(X_train, y_train)

# Évaluation du Modèle
# Prédictions
y_train_pred = rf_model.predict(X_train)
y_test_pred = rf_model.predict(X_test)

# Métriques
train_mse = mean_squared_error(y_train, y_train_pred)
test_mse = mean_squared_error(y_test, y_test_pred)
train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)

print(f"Train MSE: {train_mse:.2f}, R²: {train_r2:.2f}")
print(f"Test MSE: {test_mse:.2f}, R²: {test_r2:.2f}")

# Importance des Variables
import matplotlib.pyplot as plt

# Noms des features après OneHotEncoding
feature_names = preprocessor.named_transformers_['cat'].get_feature_names_out(['Jeux', 'Genre', 'Classe'])
feature_names = np.concatenate([['Revenu'], feature_names])

# Importance des features
importances = rf_model.feature_importances_

plt.figure(figsize=(10, 6))
plt.barh(feature_names, importances)
plt.title("Importance des Variables dans le Modèle Random Forest")
plt.show()

# Prédiction sur un Nouvel Exemple
# Création d'un nouvel exemple
new_data = pd.DataFrame({
    'Revenu': [300000],
    'Jeux': ['football'],
    'Genre': ['M'],
    'Classe': [1]
})

# Prétraitement
new_data_processed = preprocessor.transform(new_data)

# Prédiction
prediction = rf_model.predict(new_data_processed)
print(f"\nPrédiction du résultat pour le nouvel exemple: {prediction[0]:.2f}")