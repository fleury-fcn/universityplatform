🇫🇷 Version française · 🇬🇧🇺🇸 [English version](README.md)

# 🎓 ISTA — l'application étudiante de l'Institut de Statistique Appliquée

Application web « tout l'institut dans la poche » pour l'**Institut de Statistique Appliquée (ISTA)**,
Université du Burundi. Inspirée de l'application *Lilu* de l'Université de Lille, elle est pensée pour
la réalité de l'ISTA : smartphones Android d'entrée de gamme, connexions lentes ou instables,
hébergement à faible coût.

> ⚠️ Les données livrées sont des **données de démonstration** (badge « DEMO »). Voir
> [DONNEES_A_COMPLETER.md](DONNEES_A_COMPLETER.md) avant toute mise en service.

---

## ✨ Fonctionnalités

| Module | Étudiant | Enseignant | Administration |
|---|---|---|---|
| **Accueil** | cours du jour, dernières actualités | ses séances du jour | tableau de bord |
| **Actualités** | lecture, filtres par catégorie | lecture | publication, ciblage par promotion, épinglage |
| **Emploi du temps** | sa promotion, vue jour / semaine | ses séances, toutes les promotions | séances hebdomadaires, annulation / déplacement d'une séance |
| **Cours et ressources** | supports, TD, TP, anciens sujets | dépôt de documents pour ses cours | création des cours, affectation des enseignants |
| **Notes** | ses notes publiées, moyenne indicative par semestre | saisie, publication, export CSV | idem pour tous les cours |
| **Bibliothèque** | catalogue, réservation, version numérique | idem | catalogue, suivi des prêts et retours |
| **Campus** | lieux, plans, séances par salle | idem | lieux, plans, coordonnées GPS |
| **Clubs** | adhésion, annonces | idem | création, nomination des responsables |
| **Tuyaux** | partage de conseils (modérés), vote « utile » | publication directe | modération, signalements |
| **Messagerie** | messages, pièces jointes | + envoi à une promotion | idem |
| **Notifications** | dans l'application (+ push facultatif) | idem | idem |
| **Questions fréquentes** | recherche en langage courant (« comment réserver un livre ? ») | idem | rédaction des questions |
| **Mon profil** | matricule, filière, promotion, langue | | gestion des comptes, import CSV |

**Pensé pour le Burundi**
- **Hors ligne** : application installable (PWA). Emploi du temps de la semaine, actualités, plan du
  campus et liste des cours sont préchargés ; les documents téléchargés restent disponibles sans réseau.
- **Léger** : aucune dépendance externe côté navigateur (pas de CDN, pas de police web) ; une seule
  feuille de style et un petit script.
- **Langues** : français par défaut, structure prête pour l'anglais et le kirundi.
- **Accessible** : thème clair / sombre, contrastes vérifiés, navigation au clavier, mobile d'abord.

---

## 🚀 Lancer l'application (développement)

Prérequis : **Python 3.11 ou plus récent** et `make` (macOS / Linux).

```bash
git clone https://github.com/fleury-fcn/universityplatform.git
cd universityplatform
make dev
```

`make dev` crée l'environnement Python, installe les dépendances, crée la base SQLite
(`instance/ista.sqlite`), charge les données de démonstration et lance le serveur sur
<http://127.0.0.1:5001>.

<details>
<summary>Sous Windows (sans <code>make</code>)</summary>

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
$env:FLASK_APP = "run.py"
flask db upgrade
flask seed-demo
flask run
```
</details>

Pour tester sur un téléphone du même réseau Wi-Fi : `HOST=0.0.0.0 FLASK_DEBUG=false make run`, puis
ouvrir `http://<adresse-ip-de-l-ordinateur>:5001` (sans HTTPS, l'installation PWA et le hors-ligne
ne sont disponibles que sur `localhost`).

### Comptes de démonstration

Mot de passe commun : **`Demo-ISTA-2026`**

| Identifiant | Rôle | Remarque |
|---|---|---|
| `admin.demo` | Administration | accès à tout le back-office |
| `enseignant.demo` | Enseignant | responsable des cours du Master 1 SAID |
| `etudiant.demo` | Étudiant | Master 1 SAID, avec des notes fictives |
| `etudiante.demo` | Étudiante | Master 1 SAID |

> Ces comptes sont signalés sur le tableau de bord d'administration tant qu'ils sont actifs.
> **Désactivez-les avant la mise en service.**

### Tests

```bash
make test                     # SQLite en mémoire
TEST_DATABASE_URL=postgresql://utilisateur@localhost:5432/ista_test make test   # sur PostgreSQL
```

La suite couvre l'authentification, les droits d'accès de chaque rôle, la sécurité des fichiers
déposés et les fonctionnalités principales.

---

## ⚙️ Configuration

Toute la configuration passe par des variables d'environnement (fichier `.env`, jamais versionné).
Copier [.env.example](.env.example) en `.env` puis compléter.

| Variable | Rôle |
|---|---|
| `SECRET_KEY` | **obligatoire en production** ; `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `APP_ENV` | `development` (défaut) ou `production` |
| `DATABASE_URL` | vide = SQLite ; production : `postgresql://utilisateur:motdepasse@hote:5432/ista` |
| `UPLOAD_FOLDER` | dossier des fichiers déposés (défaut `instance/uploads`) — **à sauvegarder** |
| `MAX_UPLOAD_MB` | taille maximale d'un envoi (défaut 20) |
| `ALLOW_SELF_REGISTRATION` | `true` pour permettre aux étudiants de demander un compte (validé par l'admin) |
| `PASS_MARK` | note de validation sur 20 (défaut 10, à confirmer) |
| `TRUST_PROXY` | `1` si l'application est derrière un proxy HTTPS (Caddy, Nginx, PaaS) |
| `COOKIE_SECURE` | `true` (défaut) ; ne mettre `false` que sans HTTPS |
| `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_CONTACT` | notifications push facultatives (`flask push-keys`) |

---

## 🌍 Déploiement

### Option A — VPS avec Docker (recommandé)

Un petit VPS (1 vCPU, 1 Go de RAM) suffit.

```bash
git clone https://github.com/fleury-fcn/universityplatform.git && cd universityplatform
cp .env.example .env
# Renseigner au minimum : SECRET_KEY, POSTGRES_PASSWORD (et APP_ENV=production)
docker compose up -d --build
docker compose exec web flask create-admin      # premier compte administrateur
```

L'application écoute sur le port 8000 ; PostgreSQL et les fichiers déposés sont conservés dans des
volumes Docker (`pgdata`, `uploads`). Placer un proxy HTTPS devant, par exemple
[Caddy](https://caddyserver.com) (certificat automatique) :

```
ista.example.bi {
    reverse_proxy 127.0.0.1:8000
}
```

### Option B — VPS sans Docker

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
export APP_ENV=production SECRET_KEY=... DATABASE_URL=postgresql://... TRUST_PROXY=1
.venv/bin/flask --app run.py db upgrade
.venv/bin/flask --app run.py create-admin
.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 run:app   # à lancer via systemd
```

### Option C — Plateforme (PaaS)

Toute plateforme qui sait construire un `Dockerfile` et fournir PostgreSQL convient (Render, Railway,
Fly.io…). Vérifier les conditions et quotas des offres gratuites au moment du choix. Définir
`APP_ENV=production`, `SECRET_KEY`, `DATABASE_URL`, `TRUST_PROXY=1`, et un **disque persistant**
monté sur `UPLOAD_FOLDER` (sinon les fichiers déposés sont perdus à chaque redéploiement).

### Sauvegardes

À sauvegarder régulièrement : la base PostgreSQL (`pg_dump`) **et** le dossier `UPLOAD_FOLDER`.

```bash
docker compose exec db pg_dump -U ista ista > sauvegarde-$(date +%F).sql
docker compose cp web:/data/uploads ./uploads-$(date +%F)
```

---

## 🧭 Architecture

```
app/
├── __init__.py        fabrique de l'application, enregistrement des modules
├── config.py          configuration (variables d'environnement uniquement)
├── core/              sécurité (rôles, CSP, redirections), fichiers, dates, gabarits
├── models/            modèles SQLAlchemy, un fichier par domaine
├── services/          logique partagée : comptes, notifications, push
├── auth/ profile/ admin/ news/ schedule/ courses/ grades/
├── library/ campus/ clubs/ tips/ messages/ notifications/ files/
├── templates/         gabarits Jinja (un dossier par module) + sw.js (service worker)
├── static/            app.css, app.js, icônes SVG, manifeste PWA
└── translations/      catalogues en / rn
migrations/            migrations Alembic (une par fonctionnalité)
tests/                 tests pytest
```

**Sécurité** : mots de passe hachés (scrypt), CSRF sur tous les formulaires, contrôle d'accès par
rôle sur chaque route, en-têtes CSP stricts (aucun script en ligne sans nonce), verrouillage après
5 échecs de connexion, sessions invalidées au changement de mot de passe, fichiers déposés vérifiés
(extension **et** contenu), stockés hors du dossier public et servis après contrôle des droits.

### Commandes utiles

| Commande | Effet |
|---|---|
| `flask create-admin` | crée un compte administrateur |
| `flask seed-demo` | charge les données de démonstration (sans doublons) |
| `flask push-keys` | génère les clés des notifications push |
| `flask translate update` / `compile` | met à jour / compile les traductions |
| `flask db migrate -m "..."` puis `flask db upgrade` | après modification d'un modèle |

### Traductions

Les textes sont rédigés en français et extraits avec Babel. Pour traduire en anglais (`en`) ou en
kirundi (`rn`) : `make translations`, compléter `app/translations/<langue>/LC_MESSAGES/messages.po`
(avec [Poedit](https://poedit.net) par exemple), puis relancer l'application — la compilation est
automatique. Une langue s'affiche via le sélecteur en bas de page ou dans « Mon profil ».

---

## 📄 Documents

- [GUIDE_ADMIN.md](GUIDE_ADMIN.md) — guide court pour l'administration de l'ISTA
- [DONNEES_A_COMPLETER.md](DONNEES_A_COMPLETER.md) — données de démonstration à remplacer
- [CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md) · [LICENSE](LICENSE) (MIT)

---

## 👤 Auteur

<img src="https://github.com/fleury-fcn.png" width="100" style="border-radius: 50%;" alt="Fleury Niyokwizera" />

**Fleury NIYOKWIZERA**
Master 1 Statistique Appliquée et Informatique Décisionnelle – ISTA, Université du Burundi
Actuellement en Master Modélisation des Données (parcours Intelligence Artificielle) – Université de Lille

[![GitHub](https://img.shields.io/badge/GitHub-fleury--fcn-181717?style=flat&logo=github&logoColor=white)](https://github.com/fleury-fcn)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Fleury_Niyokwizera-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/fleury-niyokwizera-2a9436291)
[![Email](https://img.shields.io/badge/Email-fleuryniyokwizera2021%40gmail.com-D14836?style=flat&logo=gmail&logoColor=white)](mailto:fleuryniyokwizera2021@gmail.com)
