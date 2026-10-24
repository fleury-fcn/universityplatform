# Guide de l'administration ISTA

Ce guide explique les tâches courantes. Toutes se font depuis l'application, menu
**Accueil → Administration** (visible uniquement pour les comptes « Administration »).

---

## Premier démarrage

1. Sur le serveur : `flask create-admin` (identifiant, nom, mot de passe d'au moins 8 caractères).
2. Se connecter, puis vérifier **Filières et promotions** (voir ci-dessous).
3. Importer les comptes, saisir salles, cours et emplois du temps.
4. Quand tout est prêt : `flask purge-demo` pour retirer les données de démonstration.

## Utilisateurs

**Administration → Utilisateurs**

- **Créer un compte** : bouton « Nouveau ». Pour un étudiant, le **matricule** est obligatoire et sert
  d'identifiant de connexion ; choisir sa **promotion**.
- **Importer en masse** : bouton « Importer », fichier CSV (Excel → « Enregistrer sous » → CSV) :

  ```
  matricule;prenom;nom;email;promotion;role
  21A0001;Aline;Exemple;;M1-SAID;etudiant
  ENS01;Jean;Exemple;jean@exemple.bi;;enseignant
  ```

  Si une ligne est fausse, rien n'est importé et les erreurs sont listées. Sinon, un fichier
  `comptes_crees.csv` est téléchargé avec les **mots de passe provisoires** : à distribuer en main
  propre, puis à supprimer.
- **Mot de passe oublié** : ouvrir le compte → « Générer un mot de passe provisoire ». La personne
  devra le changer à sa prochaine connexion.
- **Départ d'un étudiant / enseignant** : décocher « Compte actif » (la personne est déconnectée
  partout ; son historique est conservé).
- **Demandes de compte** (si `ALLOW_SELF_REGISTRATION=true`) : filtre « Inactifs ou en attente »,
  bouton « Activer » après vérification du matricule.

Rôles : **Étudiant·e** (consultation), **Enseignant·e** (dépôt de documents et saisie des notes de
ses cours), **Administration** (tout). N'attribuer les deux derniers qu'après vérification.

## Filières et promotions

**Administration → Filières et promotions** : départements, filières, puis promotions (une promotion
= un niveau d'une filière pour une année, par exemple `M1-SAID`, 2026-2027).
En fin d'année : créer les promotions de la nouvelle année, rattacher les étudiants, puis décocher
« Promotion en cours » pour les anciennes.

## Actualités

**Actualités → Gérer → Nouvelle**

- Choisir une **catégorie** et les **destinataires** (tout l'institut ou une promotion).
- Cocher **Publier** : les destinataires reçoivent une notification. Sans cette case, l'actualité
  reste un brouillon invisible.
- **Épingler** garde l'actualité en haut de la liste (informations durables : contacts, horaires).
- Texte simple : laisser une ligne vide entre deux paragraphes.

## Emploi du temps

**Emploi du temps → Gérer** (choisir la promotion)

- **Séance hebdomadaire** : « Séance » → fréquence « Chaque semaine », jour, heures, salle,
  enseignant, et si besoin la période (« À partir du » / « Jusqu'au », par exemple le semestre).
- **Séance unique** (rattrapage, examen) : fréquence « Une seule fois » et la date.
- **Annuler ou déplacer une seule séance** : ouvrir l'emploi du temps au jour concerné, cliquer
  « Modifier ou annuler ce jour » sous la séance. « Rétablir la séance habituelle » annule la
  modification.
- Laisser « Prévenir les étudiants concernés » coché pour envoyer une notification.

## Cours et documents

**Cours → Gérer → Nouveau cours** : code, intitulé, promotion, semestre, crédits et **enseignant
responsable**. L'enseignant responsable peut ensuite, depuis la page du cours, déposer des documents
(supports, TD, TP, anciens sujets, corrigés) et saisir les notes. Les étudiants de la promotion sont
prévenus de chaque nouveau document.

Formats acceptés : PDF, Word, PowerPoint, Excel, OpenDocument, CSV, texte, images (20 Mo maximum).
Ne déposer que des documents dont la diffusion est autorisée.

## Notes

**Notes** → choisir le cours → session (normale ou rattrapage) → saisir (virgule ou point, de 0 à 20,
case « Absent ») → **Enregistrer**. Les étudiants ne voient rien tant que l'on n'a pas cliqué
**Publier les notes** ; ils reçoivent alors une notification. « Exporter (CSV) » produit la feuille
de notes pour archivage. La moyenne affichée aux étudiants est indicative : seul le relevé officiel
fait foi.

## Bibliothèque

**Bibliothèque → Gérer**

- « Livre » : ajouter un ouvrage (cote, nombre d'exemplaires ; 0 pour un livre uniquement numérique,
  PDF facultatif).
- Réservations : **Prêt à retirer** (l'étudiant est prévenu), **Remis** (emprunt de 14 jours),
  **Rendu**, ou **Refuser**. Les retards sont signalés en rouge.

## Campus

**Campus → Gérer** : ajouter les lieux (code, type, bâtiment, étage, capacité, indications) et
déposer un ou plusieurs **plans** (image PNG ou JPEG, idéalement moins de 500 Ko). Les coordonnées
GPS sont facultatives ; relevées sur place, elles permettent d'ouvrir le lieu dans l'application de
cartes du téléphone.

## Clubs

**Clubs → Gérer → Nouveau club**, puis sur la page du club : « Nommer responsable » (matricule ou
identifiant). Les responsables publient des annonces aux membres et voient la liste des membres.

## Tuyaux (modération)

**Tuyaux → Modération** : les conseils proposés par les étudiants y attendent validation, ainsi que
les tuyaux signalés. Ouvrir, puis **Publier** ou **Refuser / retirer** (le motif est transmis à
l'auteur). Refuser : informations fausses, données personnelles, documents protégés, propos
irrespectueux.

## Bonnes pratiques

- Ne jamais envoyer un mot de passe par un canal public ni le noter dans un fichier partagé.
- Ne jamais déposer de pièces d'identité, de mots de passe ou de fichiers `.env` dans l'application
  ou dans Git.
- Sauvegarder régulièrement la base **et** le dossier des fichiers (voir README, « Sauvegardes »).
- Après une mise à jour du code : `flask db upgrade` (fait automatiquement par Docker).
