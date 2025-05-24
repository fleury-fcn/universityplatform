import os
import sys


'''liste1 = []

n = int(input('Enter the size :'))
for i in range(n):
    element = int(input('Write the element :'))
    liste1.append(element)

print(f"Notre liste 1 des elements est la suivante : {liste1}\n\n")

print('###############################################################################')

liste2 = []

n = int(input('Enter the size :'))
for i in range(n):
    element = int(input('Write the element :'))
    liste2.append(element)

print(f"Notre liste 2 des elements est la suivante : {liste2}")

print('#############################################################')
print('La concatenation de deux liste est :')

liste1.extend(liste2)
print(liste1)



print(f'La Somme des elements de la liste1 est :{sum(liste1)}')
print(f'La Somme des elements de la liste1 est :{(liste1)}')
print(f'La Somme des elements de la liste1 est :{sum(liste1)}')

print(f'Calculer la somme des elements de la liste :{liste1}')
Somme = 0

for i in liste1:
    Somme = Somme + i
    
print(f'La somme des elements est : {Somme}\n\n')


print(f'Afficher la moyenne les elements de la liste :{liste1}')
Somme = 0
for i in liste1:
    Somme = Somme + i
    moyenne = Somme/n
print(f'La moyenne des elements est : {moyenne}\n\n')

print(f'Calculer le produit des elements de la liste :{liste1}')
produit = 1

for i in liste1:
    produit = produit * i
    
print(f'Le produit des elements est : {produit}\n\n')

print(f'Les elements de la liste {liste1 } par ordre decroissant est\n')
decroissant = liste1.sort(reverse=True)
print(decroissant)


print(f'Afficher le nombre d element nul, negatif dans: {liste1}\n\n')

for indice,element1 in liste1:
    if element1 == 0:
        print(f"Le nombre d'element nul est :{indice}:{element1}")'''
    


'''row = int(input('Entrer le nombre de ligne :'))
col = int(input('Entrer le nombre de colonne :'))

a = []
for i in range(row):
    a.append([0]*col)
    for j in range(col):
        a[i][j] = int(input('Enter les elements de la matrice'))

print(a)

k = 1
for i in range(row):
    for j in range(col):
        if a[i][j] %2 != 0:
            produit = k * a[i][j]
print(f'Le produit des elements impaires des la matrice est: {produit}')'''
'''
import numpy as np

a = np.array([[13,4,7,6], [0,5,2,4], [11,2,1,1]])
print(a)


# Supprimer la 3ème ligne de la matrice a
a = np.delete(a, 2, axis=0)
print("Matrice après suppression de la 3ème ligne:")
print(a)

# Supprimer la dernière colonne de la matrice a
a = np.delete(a, -1, axis=1)
print("Matrice après suppression de la dernière colonne:")
print(a)

# Trier les éléments des lignes de la matrice
a = np.sort(a, axis=1)
print("Matrice après tri des éléments des lignes:")
print(a)'''


'''import math

def resoudre_equation_second_degre(a, b, c):
    """
    Résout une équation du second degré de la forme ax² + bx + c = 0
    Retourne les solutions sous forme de tuple
    """
    if a == 0:
        if b == 0:
            if c == 0:
                return "Tous les réels sont solutions"
            else:
                return "Pas de solution"
        else:
            return (-c / b,)
    
    discriminant = b**2 - 4*a*c
    
    if discriminant > 0:
        x1 = (-b - math.sqrt(discriminant)) / (2*a)
        x2 = (-b + math.sqrt(discriminant)) / (2*a)
        return (x1, x2)
    elif discriminant == 0:
        x = -b / (2*a)
        return (x,)
    else:
        partie_reelle = -b / (2*a)
        partie_imaginaire = math.sqrt(-discriminant) / (2*a)
        x1 = complex(partie_reelle, -partie_imaginaire)
        x2 = complex(partie_reelle, partie_imaginaire)
        return (x1, x2)

# Exemple d'application
print("Exemple 1: 2x² + 5x - 3 = 0")
solutions = resoudre_equation_second_degre(2, 5, -3)
print(f"Solutions: {solutions}\n")

print("Exemple 2: x² - 4x + 4 = 0")
solutions = resoudre_equation_second_degre(1, -4, 4)
print(f"Solutions: {solutions}\n")

print("Exemple 3: x² + x + 1 = 0")
solutions = resoudre_equation_second_degre(1, 1, 1)
print(f"Solutions: {solutions}\n")

print("Exemple 4: 0x² + 3x - 6 = 0")
solutions = resoudre_equation_second_degre(0, 3, -6)
print(f"Solutions: {solutions}")


#!/usr/bin/env python
# coding: utf-8

# In[12]:


import os
import sys
liste=[]
n= int(input('Entrer n, la taille de la liste'))
for i in range(n):
    element=int(input("Saisir l'element:"))
    liste.append(element)
print(liste)
print('====================================================')
liste1=[]
n1= int(input('Entrer n, la taille de la deuxieme liste'))
for i in range(n1):
    element1=int(input("Saisir l'element:"))
    liste1.append(element1)
print(liste1)
print('=================================================')
print('La concatenation de 2 liste est:')
liste.extend(liste1)
print(liste)


# In[16]:


import os
import sys
liste=[]
n= int(input("Entrer n, la taille de la liste : "))
for i in range(n):
    element=int(input("Saisir l'element:"))
    liste.append(element)
somme= sum(liste)
moyenne= somme/n
tri_croissant=sorted(liste)
tri_decroissant=sorted(liste,reverse=True)
print("La liste du tableau est:",liste)   
print("L'ordre croissant de la liste est :",tri_croissant)
print("L'ordre décroissant de la liste est :",tri_decroissant)
print("La somme est:",somme)
print("La moyenne est:",moyenne)


# In[6]:


import os 
import sys 
row=int(input("Entrez le nombre de ligne: "))
col=int(input("Entrez le nombre de colonne: "))
a=[]
for i in range(row):
    a.append([0]*col)
    for j in range(col):
        a[i][j]=int(input("Enrez les éléments de la matrice"))
print(a)
k=0
p=0
for i in range(row):
    for j in range(col):
        if a[i][j]==0:
            k=k+1                                             
print("Le nombre d'elements nul est",k)
p=1
for i in range(row):
    for j in range(col):
        if a[i][j]%2!=0:
            p=p*a[i][j] 
print("Le produit des éléments impairs est",p)


# In[24]:


import numpy as np 
a=np.array([[1,2,5],[3,2,1],[1,1,4],[7,8,9]])
print(a)
d=np.array([[7],[6],[4],[8]])
print("Affichage de la matrcie après l'ajout des élèments")
print(np.append(a,d,axis=1))
supp=np.delete(a,2,axis=0)
print("Supprimer la ligne 3: \n",supp)
tri_cr=np.sort(a,axis=0)
print("Matrice triée est :\n",tri_cr)


# In[52]:


import numpy as np

# Coefficients du système d'équations
A = np.array([
    [2, 3, 8],
    [3, -7, 0],
    [-3, 9, 11]
])

# Termes constants
B = np.array([9, 10, 13])

# Calculer le déterminant de la matrice A
det_A = np.linalg.det(A)

if det_A == 0:
    print("Le système n'a pas de solution unique.")
else:
    # Calculer les déterminants pour x, y, z
    A_x = A.copy()
    A_y = A.copy()
    A_z = A.copy()
    
    # Remplacer la première colonne par B pour x
    A_x[:, 0] = B
    det_x = np.linalg.det(A_x)
    
    # Remplacer la deuxième colonne par B pour y
    A_y[:, 1] = B
    det_y = np.linalg.det(A_y)
    
    # Remplacer la troisième colonne par B pour z
    A_z[:, 2] = B
    det_z = np.linalg.det(A_z)
    
    # Calculer les valeurs de x, y, z
    x = det_x / det_A
    y = det_y / det_A
    z = det_z / det_A
    
    # Afficher la solution avec 2 chiffres après la virgule
    print(f"La solution est : x = {x:.2f}, y = {y:.2f}, z = {z:.2f}")


# In[30]:



import numpy as np

# Coefficients du système d'équations
A = np.array([
    [2, 3, 8],    # Coefficients de la première équation
    [3, -7, 0],   # Coefficients de la deuxième équation
    [-3, 9, 11]   # Coefficients de la troisième équation
])

# Termes constants
B = np.array([9, 10, 13])

# Résoudre le système d'équations
solution = np.linalg.solve(A, B)

# Afficher la solution
x, y, z = solution
print(f"La solution est : x = {x:.2f}, y = {y:.2f}, z = {z:.2f}")


# In[49]:


import numpy as np

# 1. Créer la matrice a
a = np.array([[2, 3, 8],[3, -7, 5],[2, 9, 11]])
print("La matrice est : \n",a)

# 2. Supprimer la 3ème ligne de la matrice a
a = np.delete(a, 2, axis=0)
print("Matrice après la suppression de la 3 ligne est : \n",a)
# 3. Supprimer la dernière colonne de la matrice a
a = np.delete(a, -1, axis=1)
print("Matrice après la suppression de la dernière colonne est : \n",a)
# 4. Trier les éléments des lignes de la matrice a
a = np.sort(a, axis=1)
print("La matrice triée est : \n",a)
# 5. Transformer la matrice de dimension (n) en matrice de dimension (m, t)
# (ici nous allons simplement reshaper en 2 lignes et 1 colonne, par exemple)
a = a.reshape(2, 2)

# 6. Ajouter une ligne et une colonne à la matrice (m, t)
a = np.vstack([a, [3, 2]])  # Ajouter une ligne 
a = np.column_stack([a, [2, 4, 5]])  # Ajouter une colonne
print("La matrice après l'ajout d'une ligne et une colonne est :\n",a)
# 7. Afficher la somme des colonnes
print("La somme des colonnes est :\n")
print(np.sum(a, axis=0))

# 8. Afficher la somme des lignes
print("La somme des lignes :\n")
print(np.sum(a, axis=1))

# 9. Afficher les éléments minimaux par lignes ainsi que la moyenne des lignes
print("Les éléments minimaux par lignes :\n")
print(np.min(a, axis=1))
print("La moyenne des lignes :\n")
print(np.mean(a, axis=1))

# 10. Afficher les éléments maximaux par colonnes ainsi que la moyenne des colonnes
print("Les éléments maximaux par colonnes :\n")
print(np.max(a, axis=0))
print("La moyenne des colonnes :\n")
print(np.mean(a, axis=0))

# 11. Afficher la transposée et la matrice symétrique de a
transposed_a = np.transpose(a)
symmetric_a = (a + transposed_a) / 2  # Matrice symétrique
print("La transposée de a :\n")
print(transposed_a)
print("La matrice symétrique de a :\n")
print(symmetric_a)

# 12. Afficher le déterminant de a, ainsi que le produit de a et d
# Pour le produit, nous avons besoin d'une matrice d compatible
d = np.array([[1, 2], [3, 4], [5, 6]])  # Exemple de matrice d (3x2)
product_a_d = np.dot(a, d[:a.shape[1], :])  # Produit des matrices a et d
print("Le produit de la matrice est :\n",a)
# Calcul du déterminant seulement si a est carrée
if a.shape[0] == a.shape[1]:
    det_a = np.linalg.det(a)
    print("Le Déterminant de a est :\n")
    print(det_a)
else:
    print("La matrice a n'est pas carrée, pas de déterminant.")

print("Le produit de a et d est :\n")
print(product_a_d)


# In[ ]:

'''

import pandas as pd
d = {'colonne A' : pd.Series([111, 222, 333, 444], index=['a', 'b', 'c', 'd'] ), 
     'colonne B' : pd.Series([11, 22, 3, 484], index=['a', 'b', 'c', 'd'])}

df = pd.DataFrame(d)

print(df)

dloc = df.loc['b']
print(dloc)


# Creation d'une base de donnees
data0 = {
    'Nom':['Fleury', 'Cherissa', 'Jimy', 'Fedor', 'Aline', 'Alexendre'],
    'Resultas':[20, 14, 6, 18, 17, 10],
   'Revenu':[2000000, 150000, 450000, 35000, 560000, 450000],
   'jeux':['Football', 'Tenis', 'Rigbey', 'course', 'Natation', 'Danse'],
   'Genre':['M', 'F', 'M', 'M', 'F', 'M'],
   
}

data0 = pd.DataFrame(data= data0)



























































