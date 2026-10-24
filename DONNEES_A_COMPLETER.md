# Données à compléter avant la mise en service

L'application n'invente aucune information officielle. Tout ce qui n'était pas déjà présent dans
l'ancien code est une **donnée de démonstration** : elle porte un badge **DEMO** dans l'interface
(champ `is_demo` en base) et se retire en une commande :

```bash
flask purge-demo      # supprime les contenus DEMO et désactive les comptes de démonstration
```

Les données de démonstration sont définies dans [app/seed.py](app/seed.py) (`flask seed-demo`).

---

## 1. Reprises de l'ancien code — à confirmer

Ces informations figuraient dans l'ancienne plateforme. Elles **ne sont pas** marquées DEMO, mais
leur exactitude n'a pas été vérifiée. À corriger depuis **Administration → Filières et promotions**
et **Clubs**.

| Donnée | Valeur reprise | À vérifier |
|---|---|---|
| Départements | Actuariat (ACTU), Génie Statistique (GENSTAT), Probabilités et Statistique (PROBA) | noms officiels, descriptions |
| Filières | ARISK, APRED, SECO, SDATA, PROBSTATS (licence) ; MACTU, MSAID, MMSP (master) | liste complète, rattachements |
| Promotions | BAC2-ARISK-A, BAC3-APRED-A, BAC2-SECO-A, BAC3-SDATA-A, BAC3-PROBA-A, M1-ACTUFIN, M1-SAID, M1-MSP | promotions manquantes (BAC1, M2…), année académique (calculée automatiquement) |
| Clubs | Informatique Décisionnelle, Actuariat Club, Actualité Économique, Génies en Herbe, English Club ISTA, ISTA Entrepreneurs | existence actuelle, fréquences, contacts, responsables (orthographe des descriptions corrigée) |
| Logo | logo de l'Université du Burundi (`app/static/img/logo.png`) | autorisation d'usage, logo propre à l'ISTA éventuel |
| Coordonnées | « RN6 ISTA, Nyamugerera, Burundi », +257 62 495 566, lundi–vendredi 8h–18h (non affichées dans l'application) | à confirmer avant de les publier, par exemple dans une actualité épinglée |

**Volontairement non repris** : les noms de personnes réelles présents dans l'ancien code
(doyenne, secrétariat, enseignants, étudiants), l'adresse `contact@openista.edu` (domaine non
officiel), les dates de concours d'admission, et tous les fichiers déposés (déplacés hors du dépôt,
dans `instance/legacy_files/` sur la machine de développement).

## 2. Données de démonstration (badge DEMO)

| Donnée | Contenu | À remplacer par |
|---|---|---|
| Comptes | `admin.demo`, `enseignant.demo`, `etudiant.demo`, `etudiante.demo` (mot de passe public) | vrais comptes (import CSV) ; **désactiver ces comptes** |
| Actualités | 3 annonces d'exemple | annonces réelles |
| Catégories d'actualités | Annonces, Examens, Vie étudiante, Événements | catégories souhaitées (non marquées DEMO, modifiables) |
| Salles | Amphithéâtre, Salle 1, Laboratoire informatique, Bibliothèque (toutes « DEMO ») | liste réelle des lieux, bâtiments, capacités, coordonnées GPS relevées sur place |
| Plans du campus | aucun | photo ou schéma du campus (Campus → Gérer) |
| Emploi du temps | 5 séances hebdomadaires fictives pour le Master 1 SAID | emplois du temps réels de chaque promotion |
| Cours | 10 cours ; 8 intitulés repris des UE de l'ancien code, **crédits et semestres non vérifiés** | maquettes officielles (codes, crédits, semestres, enseignants) |
| Notes | notes fictives des deux comptes étudiants de démonstration | aucune note réelle ne doit être versionnée ; elles sont saisies dans l'application |
| Bibliothèque | 6 livres aux auteurs fictifs (repris de l'ancien `init_books.py`) | catalogue réel, cotes, nombre d'exemplaires |
| Tuyaux | 3 conseils d'exemple | contributions des étudiants |

La **FAQ** contient 8 questions d'aide à l'utilisation de l'application (exactes, non marquées DEMO).
Les questions sur la vie à l'ISTA (inscriptions, frais, calendrier académique, horaires des
services, logement, transport…) sont **à rédiger par l'administration** (FAQ → Gérer).

## 3. Règles à valider par l'ISTA

Ces règles sont des choix par défaut, simples à modifier :

| Règle | Valeur par défaut | Où la changer |
|---|---|---|
| Note de validation d'un cours | 10/20 | variable `PASS_MARK` |
| Moyenne semestrielle | pondérée par les crédits ; absence comptée 0 ; la note de rattrapage remplace la note de session normale | `app/models/grades.py` |
| Niveaux | BAC1, BAC2, BAC3, M1, M2 (saisie libre) | formulaire des promotions |
| Durée d'un prêt de livre | 14 jours | `LOAN_DAYS` dans `app/library/routes.py` |
| Réservations simultanées | 3 par personne | `MAX_ACTIVE_RESERVATIONS` dans `app/models/library.py` |
| Messagerie | 20 destinataires max pour un étudiant, 30 messages/heure, 3 pièces jointes de 5 Mo | `app/messages/routes.py` |
| Taille des fichiers | supports de cours 20 Mo, tuyaux 10 Mo, plans 5 Mo | `app/core/files.py` et `MAX_UPLOAD_MB` |
| Inscription libre des étudiants | désactivée | variable `ALLOW_SELF_REGISTRATION` |
| Fuseau horaire | Africa/Bujumbura | variable `APP_TIMEZONE` |
| Mot de passe oublié | réinitialisation par l'administration (pas d'e-mail) | — |

## 4. Traductions

Les catalogues anglais (`app/translations/en/`) et kirundi (`app/translations/rn/`) sont prêts mais
**non traduits** : l'application s'affiche en français tant qu'une traduction manque. Le kirundi doit
être rédigé par une personne qui le parle ; aucune traduction automatique n'a été ajoutée.

## 5. Avant l'ouverture : liste de contrôle

- [ ] Secrets régénérés (l'ancien `.env` a été publié) et `SECRET_KEY` de production définie
- [ ] `flask create-admin` pour le premier compte administrateur
- [ ] Départements, filières et promotions vérifiés
- [ ] Comptes réels importés (Administration → Utilisateurs → Importer)
- [ ] Salles, plans, cours et emplois du temps saisis
- [ ] `flask purge-demo` exécuté
- [ ] Sauvegardes de la base et du dossier des fichiers planifiées
