import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


print('\n\n######## Importation des donnees Excel sous format .csv #################\n')
# Importation des donnees Excel du format CSV 
data = pd.read_csv('~/projets/OpenISTA/coursISTA/data.csv')
print(f'{data}\n \n')

print('\n\n########## Selectionner une variable cible dans le dataset ###############\n')
# dans cette base des donnes cree Selectionner une variable cibre et l'afficher 
data1 = data['Resultats']
print(f'les donnees de la variable resultats\n {data1}\n\n')

print('\n\n######## Afficher les statistiques descriptibes pour la base des donnees .csv #################\n')
# Affiche les statistiques descriptibes pour la base des donnees
state = data.describe()
print(f'les statistiques descriptives sont :\n {state}\n\n')

print('\n\n######## Afficher les elements de la ligne 3 #################\n')
# Afficher les elements de la ligne 3
ligne3 = data.iloc[3]
print(f'les elements de la ligne 3 sont : \n {ligne3}\n\n')

print('\n\n######## Afficher les 4 dernieres elements de la base des donnees #################\n')
# Afficher les 4 derniers elements de la base des donnees
elements4 = data.tail(4)
print(f'Les 4 derniers elements sont: \n {elements4}\n\n')

print('\n\n######## Fonction de trier par ligne #################\n')
# Donnees tries par ligne
data_tries = data.sort_index()
print(f'les elements de la base tries sont: \n {data_tries}\n \n ')

print('\n\n######## Fonction de trier par colonne #################\n')
# Donnees tries par Revenus
data_tries_revenus = data.sort_values(by= 'Revenu')
print(f'les elements de la base tries par Valeur (Revenu):\n {data_tries_revenus}\n \n' )

print('\n\n######## Afficher les 4 premiers elements #################\n')
# Afficher les 4 premiers elements
data_4_premiers_elements = data.head(4)
print(f'les 4 premiers elements sont :\n {data_4_premiers_elements}\n \n')

print('\n\n######## Transposer la dataframe #################\n')
# Transposer ma dataframe
data_transposed = data.T
print(f'La base des donnees Transoposees est :\n {data_transposed}\n \n')

print('\n\n######## Mettre les donnees en valeur Absolue #################\n')
# La variable revenu  en valeur abslue 
data_abs = data1.abs()
print(f'La variable revenu en valeur Absolue est :\n {data_abs}\n \n')

print('\n\n######## Fonctio produit #################\n')
# Le produit de tous les revenus
data_prod = data1.prod()
print(f'Le produit des revenus est : \n {data_prod} \n \n')

print('\n\n######## Compter le nombre de revenu disponible dans la dataframe #################\n')
# Compter le nombre de revenu disponible dans la dataframe
data_revenus_count = data1.count()
print(f'Le nombre de revenu dispo dans la base des donnees est :\n {data_revenus_count}\n \n')

print('\n\n######## Fonction de la somme cummulee de revenu #################\n')
# La somme cummulee de revenu
data_revenu_somme_cummule = data1.cumsum()
print(f'La somme cummulee de la revenu est :\n {data_revenu_somme_cummule}\n \n')

print('\n\n######## Fonction du produit cummule de revenu #################\n')
# La produit Cummule de revenu
data_revenu_produit_cummule = data1.cumprod()
print(f'Le produit cummule de revenu est :\n{data_revenu_produit_cummule}\n \n')

print('\n\n######## Fonction de verification des valeurs manquantes #################\n')
# Verification des valeurs manquantes
data_valeur_manquante = data.notnull()
print(f'Existance des Valeurs Manquantes, si True : Pas de valeur manquante :\n {data_valeur_manquante}\n \n')

print('\n\n######## Fonction de suppression Suppression des valeurs manquantes #################\n')
# Suppression des valeurs manquantes
data_VM_dropped = data.dropna()

print('\n\n######## Comparaison des % par colonne #################\n')
# Comparaison des % par colonne
a = data1.pct_change()

print('\n\n######## Covariance entre Revenus et resultats #################\n')
# Covariance entre Revenus et resultats
data_Covariance = data['Resultats'].cov(data['Revenu'])
print(f'La covariance entre Resultats et revenu est:\n {data_Covariance}\n \n')

print('\n\n######## Correlation entre Revenus et resultats #################\n')
# Correlation entre Revenus et resultats
data_Covariance = data['Resultats'].corr(data['Revenu'])
print(f'La correlation entre Resultats et revenu est:\n {data_Covariance}\n \n')

print('\n\n######## Grouper les elements du groupe par nom #################\n')
# Grouper les elements du groupe par nom
data_grouped_by_nom = data.groupby('Nom')

print('\n\n######## Concatener deux dataframes #################\n')
# Concatener deux dataframes
data0 = data
data_concat = pd.concat([data, data0])
print(f'Resultats de la concatenation :\n {data_concat}\n\n')

print('\n\n######## Diagramme de Bar des resulats #################\n')
# Generer le diagramme de Bar des resultats
plt.figure(figsize=(10,6))
sns.barplot(x='Nom', y='Revenu', data= data, palette='viridis')
plt.title('Revenu par Personne')
plt.xlabel('Nom')
plt.ylabel('Revenu')
plt.xticks(rotation =45)
plt.show()

print('\n\n######## Generation de lhistogramme #################\n')
# Generer histogramme des resultats
plt.figure(figsize=(8,6))
sns.histplot(data['Resultats'], bins=5, kde= True, color='skyblue')
plt.title('Histogeamme de resultats')
plt.xlabel('Resultats')
plt.ylabel('Frequence')
plt.show()

print('\n\n######## Generation de boite a moustache #################\n')
# Generer la boite a moustache pour les variables jeux et genre
plt.figure(figsize=(6,4))
sns.boxplot(x='Genre', y='Jeux', data= data, palette='pastel')
plt.xlabel('Genre')
plt.ylabel('Nombre de Jeux')
plt.show()

print('\n\n######## Generation des nuages des points #################\n')
# Generer les nuages ges points
plt.figure(figsize=(6,4))
sns.scatterplot(x='Revenu', y='Resultats', hue='Genre', data= data, size=100)
plt.title('Revenu vs Resultats')
plt.xlabel('Revenu')
plt.ylabel('Resultats')
plt.grid(True)
plt.show()

print('\n\n######## Distribution de violon qui illustre distribution des Revenus par Genre #################\n')
# Distribution des Revenus par Genre
plt.figure(figsize=(8,6))
sns.violinplot(x='Genre', y='Revenu', data= data, palette='muted')
plt.title('Distribution des Revenus Par Genre')
plt.xlabel('Genre')
plt.ylabel('Revenus')
plt.show()









