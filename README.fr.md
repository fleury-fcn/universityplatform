🇬🇧🇺🇸 [English version](README.md) · 🇫🇷 Version française

# 🎓 OpenISTA – Plateforme Universitaire de Gestion de Campus

**OpenISTA** est une plateforme web complète de gestion universitaire développée pour l'**Institut de Statistiques Appliquées (ISTA)**, Pôle d'Excellence de l'**Université du Burundi**, dans le cadre du projet de fin de **Master 1 en Statistique Appliquée et Informatique Décisionnelle**.

L'objectif : concevoir et développer, de bout en bout, un système capable de gérer l'ensemble des services administratifs et académiques d'un campus universitaire — étudiants, enseignants, cours, bibliothèque, vie associative et communication interne.

---

## 📌 Contexte académique

Ce projet a été réalisé individuellement pour mettre en pratique les compétences acquises dans plusieurs enseignements du Master :

- **Bases de données** – conception relationnelle, modélisation, migrations
- **Programmation avancée (Python / Flask)** – architecture back-end, logique métier
- **Génie logiciel** – structuration du code, gestion de projet, bonnes pratiques
- Autres enseignements du tronc commun informatique décisionnelle

---

## ✨ Fonctionnalités principales

La plateforme couvre l'ensemble du cycle de vie universitaire d'un campus :

### 👨‍🎓 Gestion académique
- Gestion des dossiers étudiants
- Gestion des enseignants et de leurs affectations
- Gestion des cours et programmes

### 📚 Bibliothèque
- Catalogue et gestion des ouvrages disponibles
- Suivi des emprunts (initialisation via `init_books.py`)

### 🏛️ Vie de campus
- Gestion des clubs et associations étudiantes (`init_clubs.py`)
- Espace de partage de conseils/ressources entre étudiants (« tuyaux »)

### 💬 Communication
- Système de messagerie interne avec gestion des pièces jointes
- Notifications entre utilisateurs

---

## 🛠️ Stack technique

| Composant | Technologie |
|---|---|
| Back-end | Python / Flask |
| Base de données | PostgreSQL |
| Migrations | Flask-Migrate / Alembic |
| Front-end | HTML, CSS, Jinja2 |
| Gestion des dépendances | pip / requirements.txt |

---

## 📁 Structure du projet

```
universityplatform/
├── app/                        # Cœur applicatif (routes, modèles, logique métier)
├── migrations/                 # Historique des migrations de base de données
├── static/uploads/messages/    # Fichiers joints à la messagerie interne
├── work/                       # Modules complémentaires
├── init_books.py               # Peuplement initial – bibliothèque
├── init_clubs.py                # Peuplement initial – clubs
├── init_courses.py             # Peuplement initial – cours
├── init_tuyaux.py              # Peuplement initial – ressources étudiantes
├── run.py                      # Point d'entrée de l'application
└── requirements.txt             # Dépendances Python
```

---

## 🚀 Installation et lancement en local

```bash
# 1. Cloner le dépôt
git clone https://github.com/fleury-fcn/universityplatform.git
cd universityplatform

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate      # sous Windows : venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env          # puis renseigner vos propres identifiants PostgreSQL

# 5. Initialiser la base de données
flask db upgrade

# 6. (Optionnel) Peupler la base avec des données de démonstration
python init_books.py
python init_clubs.py
python init_courses.py
python init_tuyaux.py

# 7. Lancer l'application
python run.py
```

---

## 🎯 Compétences mises en œuvre

- Conception et modélisation de bases de données relationnelles
- Développement back-end avec Flask (routing, ORM, authentification)
- Gestion de migrations de schéma de base de données
- Architecture logicielle modulaire
- Gestion de projet en autonomie, du cahier des charges à la livraison

---

## 👤 Auteur

<img src="https://github.com/fleury-fcn.png" width="100" style="border-radius: 50%;" alt="Fleury Niyokwizera" />

**Fleury NIYOKWIZERA**
Master 1 Statistique Appliquée et Informatique Décisionnelle – ISTA, Université du Burundi
Actuellement en Master Modélisation des Données (parcours Intelligence Artificielle) – Université de Lille

[![GitHub](https://img.shields.io/badge/GitHub-fleury--fcn-181717?style=flat&logo=github&logoColor=white)](https://github.com/fleury-fcn)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Fleury_Niyokwizera-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/fleury-niyokwizera-2a9436291)
[![Email](https://img.shields.io/badge/Email-fleuryniyokwizera2021%40gmail.com-D14836?style=flat&logo=gmail&logoColor=white)](mailto:fleuryniyokwizera2021@gmail.com)
