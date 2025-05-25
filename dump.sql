-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: localhost    Database: OpenIsta
-- ------------------------------------------------------
-- Server version	8.0.42-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activity_logs`
--

DROP TABLE IF EXISTS `activity_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action` varchar(500) NOT NULL,
  `details` text,
  `timestamp` datetime DEFAULT NULL,
  `ip_address` varchar(50) DEFAULT NULL,
  `entity_type` varchar(50) DEFAULT NULL,
  `entity_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_activity_logs_timestamp` (`timestamp`),
  CONSTRAINT `activity_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `utilisateurs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_logs`
--

LOCK TABLES `activity_logs` WRITE;
/*!40000 ALTER TABLE `activity_logs` DISABLE KEYS */;
INSERT INTO `activity_logs` VALUES (1,2,'Notification envoyée: Utiliser bien cette resources mes amis',NULL,'2025-05-21 20:09:05',NULL,NULL,NULL),(2,1,'Notification envoyée: Histoire d\'innovation',NULL,'2025-05-23 12:58:03',NULL,NULL,NULL),(3,1,'Notification envoyée: Encouragement',NULL,'2025-05-23 15:28:32',NULL,NULL,NULL),(4,1,'Maintenance système: restart_app',NULL,'2025-05-24 13:49:32',NULL,NULL,NULL),(5,1,'Maintenance système: clear_cache',NULL,'2025-05-24 13:52:36',NULL,NULL,NULL),(6,1,'Désactivation de l\'utilisateur fidianiyomukiza@ista.ma',NULL,'2025-05-24 13:58:25',NULL,NULL,NULL),(7,1,'Activation de l\'utilisateur fidianiyomukiza@ista.ma',NULL,'2025-05-24 13:58:32',NULL,NULL,NULL),(8,1,'Notification envoyée: Encouragement',NULL,'2025-05-24 17:06:22',NULL,NULL,NULL),(9,2,'Modification de l\'utilisateur niyonkurucherissa@gmail.com',NULL,'2025-05-24 17:08:07',NULL,NULL,NULL),(10,1,'Activation de l\'utilisateur niyonkurucherissa@gmail.com',NULL,'2025-05-24 17:10:05',NULL,NULL,NULL),(11,1,'Mise à jour des paramètres système',NULL,'2025-05-24 18:05:01',NULL,NULL,NULL),(12,1,'Mise à jour des paramètres système',NULL,'2025-05-24 18:07:16',NULL,NULL,NULL),(13,1,'Maintenance système: clear_cache',NULL,'2025-05-24 18:10:10',NULL,NULL,NULL),(14,1,'Maintenance système: restart_app',NULL,'2025-05-24 18:10:14',NULL,NULL,NULL);
/*!40000 ALTER TABLE `activity_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `addsyllabus`
--

DROP TABLE IF EXISTS `addsyllabus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `addsyllabus` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(10) NOT NULL,
  `title` varchar(200) NOT NULL,
  `credits` int NOT NULL,
  `department` varchar(50) NOT NULL,
  `year` int NOT NULL,
  `semester` int NOT NULL,
  `cycle` varchar(50) NOT NULL,
  `description` text,
  `file_path` varchar(255) DEFAULT NULL,
  `file_size` int DEFAULT NULL,
  `date_ajout` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `addsyllabus`
--

LOCK TABLES `addsyllabus` WRITE;
/*!40000 ALTER TABLE `addsyllabus` DISABLE KEYS */;
INSERT INTO `addsyllabus` VALUES (1,'0007','Logivciel du Calcul Formel',0,'genie',1,1,'bac','Bon','app/static/uploads/Logiciels_de_calcul_formel.pptx',0,NULL),(2,'22222','Cryptographie et securite des donnees',0,'genie',1,1,'bac','excellent cours','app/static/uploads/Cryptographie_et_securite_des_donnees.pdf',0,'2025-05-24 17:57:00'),(3,'22222','Cryptographie et securite des donnees',0,'genie',1,1,'bac','excellent cours','app/static/uploads/Cryptographie_et_securite_des_donnees.pdf',0,'2025-05-24 17:58:06'),(4,'22222','Cryptographie et securite des donnees',0,'genie',1,1,'bac','excellent cours','app/static/uploads/Cryptographie_et_securite_des_donnees.pdf',0,'2025-05-24 17:58:29'),(5,'7777','Adminisatration Systeme',0,'probastate',1,1,'bac','bon','app/static/uploads/Administration-systeme-partie-1.pdf',0,'2025-05-24 18:00:55'),(6,'7777','Adminisatration Systeme',0,'probastate',1,1,'bac','bon','app/static/uploads/Administration-systeme-partie-1.pdf',0,'2025-05-24 18:01:44');
/*!40000 ALTER TABLE `addsyllabus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('4e6754c82a96');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `book_downloads`
--

DROP TABLE IF EXISTS `book_downloads`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `book_downloads` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `book_id` int NOT NULL,
  `download_date` date DEFAULT NULL,
  `download_count` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_book_day` (`user_id`,`book_id`,`download_date`),
  KEY `book_id` (`book_id`),
  CONSTRAINT `book_downloads_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`),
  CONSTRAINT `book_downloads_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `utilisateurs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `book_downloads`
--

LOCK TABLES `book_downloads` WRITE;
/*!40000 ALTER TABLE `book_downloads` DISABLE KEYS */;
INSERT INTO `book_downloads` VALUES (1,1,7,'2025-05-24',1);
/*!40000 ALTER TABLE `book_downloads` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `books`
--

DROP TABLE IF EXISTS `books`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `books` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) DEFAULT NULL,
  `author` varchar(100) NOT NULL,
  `description` text,
  `category` varchar(50) NOT NULL,
  `language` varchar(20) NOT NULL,
  `level` varchar(20) NOT NULL,
  `file_path` varchar(255) NOT NULL,
  `file_size` int DEFAULT NULL,
  `file_type` varchar(20) DEFAULT NULL,
  `upload_date` datetime DEFAULT NULL,
  `downloads` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `disponible` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `books_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `utilisateurs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `books`
--

LOCK TABLES `books` WRITE;
/*!40000 ALTER TABLE `books` DISABLE KEYS */;
INSERT INTO `books` VALUES (1,'Statistique Descriptive Appliquée','Jean Dupont','Manuel complet de statistique descriptive avec exercices corrigés','statistique','fr','bac','statistique_descriptive.pdf',5200,'pdf','2025-05-21 19:59:11',0,1,NULL),(2,'Théorie des Probabilités','Marie Lambert','Fondements théoriques des probabilités et applications','probabilite','fr','master','theorie_probabilites.pdf',7800,'pdf','2025-05-21 19:59:11',0,1,NULL),(3,'Actuarial Mathematics','Robert Brown','Comprehensive guide to actuarial mathematics for insurance','actuariat','en','master','actuarial_math.pdf',9100,'pdf','2025-05-21 19:59:11',0,1,NULL),(4,'Data Science with Python','Ahmed Benali','Practical introduction to data science using Python','data-science','en','master','data_science_python.pdf',6500,'pdf','2025-05-21 19:59:11',0,1,NULL),(5,'Algorithmique et Programmation','Sophie Martin','Fondamentaux de l\'algorithmique et programmation en Python','informatique','fr','bac','algorithmique_programmation.pdf',4700,'pdf','2025-05-21 19:59:11',0,1,NULL),(6,'Méthodologie de Recherche','Institut Statistique','Guide pratique pour la rédaction de mémoires et thèses','divers','fr','all','methodologie_recherche.pdf',3900,'pdf','2025-05-21 19:59:11',0,1,NULL),(7,'Optimisation Combinatoire II','Vianney','Le cours pour les ingemieurs','divers','fr','master','20250524174942_ISTA-Optimisation_combinatoire.pdf',960,'pdf','2025-05-24 15:49:43',1,1,1);
/*!40000 ALTER TABLE `books` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clubs`
--

DROP TABLE IF EXISTS `clubs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clubs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `category` varchar(50) NOT NULL,
  `banner` varchar(255) DEFAULT NULL,
  `logo` varchar(255) DEFAULT NULL,
  `meeting_frequency` varchar(100) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `admin_id` int DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_id` (`admin_id`),
  CONSTRAINT `clubs_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `utilisateurs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clubs`
--

LOCK TABLES `clubs` WRITE;
/*!40000 ALTER TABLE `clubs` DISABLE KEYS */;
INSERT INTO `clubs` VALUES (1,'Informatique Decisionnelle Club','Le club Informatique Decisionnelle de l\'ISTA où nous explorons les dernières innovations du monde Informatique, organisons des Sciences de formation pour preparer les Génies de l\'Informatique et Statistique de demain.','technologie','tech-banner.jpg','tech-logo.jpg','Réunion hebdomadaire','Intelligence Artificielle,Programmation en Python,Developpement des Applications Web et Mobile','2025-05-21 19:59:06',1,1,NULL),(2,'Actuariat Club','Le voyage dans le monde de l\'Assurance et de la finance se passe ici, il est ouvert à tout le monde qui desire avoir une tete bien faite et bien pleine en Sciences Actuarielles','science','sport-banner.jpg','sport-logo.jpg','3x/semaine','Tarification en Assurance IARD,Gestion des risques Financiers','2025-05-21 19:59:06',1,1,NULL),(3,'Club d\'Actualité Economique','Pour les passionnés de l\'actuaritité Economique, cet espace est le votre.','social','data-banner.jpg','data-logo.jpg','2x/mois','Taux d\'inflation,Crise Economique,Banques des jeunes','2025-05-21 19:59:06',1,1,NULL),(4,'Genie en Herbes','Pour devenir un intellectuel bien informé, cultivé, voici l\'endroit qui te convient.','art','eco-banner.jpg','eco-logo.jpg','1x/semaine','Rubriques Question Reponse,Histoire','2025-05-21 19:59:06',1,1,NULL),(5,'English Club ISTA','You dream to increase your English Level and become fluent like a native speaker.We are here for You.','social','art-banner.jpg','art-logo.jpg','Variable','English for Biginner,English advenced Level','2025-05-21 19:59:06',1,1,NULL),(18,'Club d\'Innovation en Statistique Appliquée et Actuariat','Le terrain des savants','sport','default-banner.jpg','default-logo.jpg','une fois dans deux semaine','Science et Informatique','2025-05-24 17:51:10',1,0,NULL);
/*!40000 ALTER TABLE `clubs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cours`
--

DROP TABLE IF EXISTS `cours`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cours` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(20) NOT NULL,
  `titre` varchar(100) NOT NULL,
  `description` text,
  `credits` int DEFAULT NULL,
  `cycle` varchar(20) DEFAULT NULL,
  `annee` int DEFAULT NULL,
  `departement` varchar(50) DEFAULT NULL,
  `parcours` varchar(50) DEFAULT NULL,
  `semestre` int DEFAULT NULL,
  `specialisation` varchar(50) DEFAULT NULL,
  `horaire` varchar(100) DEFAULT NULL,
  `lieu` varchar(100) DEFAULT NULL,
  `fichier` varchar(200) DEFAULT NULL,
  `date_ajout` datetime DEFAULT NULL,
  `professeur_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `professeur_id` (`professeur_id`),
  CONSTRAINT `cours_ibfk_1` FOREIGN KEY (`professeur_id`) REFERENCES `professeur` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cours`
--

LOCK TABLES `cours` WRITE;
/*!40000 ALTER TABLE `cours` DISABLE KEYS */;
INSERT INTO `cours` VALUES (1,'0001','Administration Systeme','Bon',4,'master',4,'genie',NULL,2,NULL,'Mardi-15h-19h','Amph1','0001_Administration-systeme-partie-1.pdf','2025-05-24 18:18:09',2);
/*!40000 ALTER TABLE `cours` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documents_inscription`
--

DROP TABLE IF EXISTS `documents_inscription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documents_inscription` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inscription_id` int NOT NULL,
  `type_document` varchar(50) NOT NULL,
  `nom_original` varchar(255) DEFAULT NULL,
  `chemin_fichier` varchar(255) NOT NULL,
  `taille_fichier` int DEFAULT NULL,
  `format_fichier` varchar(10) DEFAULT NULL,
  `est_valide` tinyint(1) DEFAULT NULL,
  `date_validation` datetime DEFAULT NULL,
  `valide_par` int DEFAULT NULL,
  `date_depot` datetime DEFAULT NULL,
  `date_maj` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `chemin_fichier` (`chemin_fichier`),
  KEY `valide_par` (`valide_par`),
  KEY `ix_documents_inscription_inscription_id` (`inscription_id`),
  CONSTRAINT `documents_inscription_ibfk_1` FOREIGN KEY (`inscription_id`) REFERENCES `inscriptions_academiques` (`id`),
  CONSTRAINT `documents_inscription_ibfk_2` FOREIGN KEY (`valide_par`) REFERENCES `utilisateurs` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documents_inscription`
--

LOCK TABLES `documents_inscription` WRITE;
/*!40000 ALTER TABLE `documents_inscription` DISABLE KEYS */;
/*!40000 ALTER TABLE `documents_inscription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inscriptions_academiques`
--

DROP TABLE IF EXISTS `inscriptions_academiques`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inscriptions_academiques` (
  `id` int NOT NULL AUTO_INCREMENT,
  `matricule` varchar(20) NOT NULL,
  `nom` varchar(50) NOT NULL,
  `prenom` varchar(50) NOT NULL,
  `genre` varchar(10) NOT NULL,
  `date_naissance` date NOT NULL,
  `email_institutionnel` varchar(100) DEFAULT NULL,
  `annee_academique` varchar(20) NOT NULL,
  `niveau` varchar(20) NOT NULL,
  `departement` varchar(50) NOT NULL,
  `specialisation` varchar(50) DEFAULT NULL,
  `filiere` varchar(50) DEFAULT NULL,
  `est_confirme` tinyint(1) DEFAULT NULL,
  `date_confirmation` datetime DEFAULT NULL,
  `est_actif` tinyint(1) DEFAULT NULL,
  `date_creation` datetime DEFAULT NULL,
  `date_mise_a_jour` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `matricule` (`matricule`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inscriptions_academiques`
--

LOCK TABLES `inscriptions_academiques` WRITE;
/*!40000 ALTER TABLE `inscriptions_academiques` DISABLE KEYS */;
INSERT INTO `inscriptions_academiques` VALUES (1,'20/03892','NIYOKWIZERA','Fleury','male','2000-12-12','adminopenista@gmail.com','2023-2024','bac2','actuariat','risques',NULL,0,NULL,1,'2025-05-23 19:41:32',NULL),(2,'20/03891','NIYONKURU','Cherissa','female','1999-12-12','niyonkurucherissa@gmail.com','2023-2024','master1','probastate','',NULL,0,NULL,1,'2025-05-24 14:24:03',NULL);
/*!40000 ALTER TABLE `inscriptions_academiques` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `members`
--

DROP TABLE IF EXISTS `members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `members` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `level` varchar(50) NOT NULL,
  `department` varchar(50) NOT NULL,
  `academic_year` varchar(20) NOT NULL,
  `joined_at` datetime DEFAULT NULL,
  `club_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `club_id` (`club_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `members_ibfk_1` FOREIGN KEY (`club_id`) REFERENCES `clubs` (`id`),
  CONSTRAINT `members_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `utilisateurs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `members`
--

LOCK TABLES `members` WRITE;
/*!40000 ALTER TABLE `members` DISABLE KEYS */;
INSERT INTO `members` VALUES (2,'Cherissa','NIYONKURU','Bac','SECO','2024-2025','2025-05-24 17:54:32',3,1),(3,'Jimmy','BIMENYIMANA','Master','SAID','2024-2025','2025-05-24 18:41:06',2,7),(4,'Fleury','NIYOKWIZERA','2ème année','Actuariat','2023-2024','2025-05-24 20:53:50',1,1);
/*!40000 ALTER TABLE `members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message_recipients`
--

DROP TABLE IF EXISTS `message_recipients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `message_recipients` (
  `message_id` int NOT NULL,
  `user_id` int NOT NULL,
  `is_deleted` tinyint(1) DEFAULT NULL,
  `read_at` datetime DEFAULT NULL,
  PRIMARY KEY (`message_id`,`user_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `message_recipients_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `messages` (`id`),
  CONSTRAINT `message_recipients_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `utilisateurs` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message_recipients`
--

LOCK TABLES `message_recipients` WRITE;
/*!40000 ALTER TABLE `message_recipients` DISABLE KEYS */;
INSERT INTO `message_recipients` VALUES (2,1,0,'2025-05-22 19:24:33'),(4,2,0,NULL),(5,2,0,NULL),(6,2,1,NULL),(7,2,0,'2025-05-23 16:01:06'),(8,2,1,NULL),(9,1,0,'2025-05-23 12:55:13'),(10,2,1,NULL),(11,2,1,NULL),(12,2,1,NULL),(13,2,1,NULL),(14,3,0,NULL),(15,1,0,'2025-05-24 18:55:38');
/*!40000 ALTER TABLE `message_recipients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sender_id` int NOT NULL,
  `subject` varchar(200) DEFAULT NULL,
  `content` text NOT NULL,
  `sent_at` datetime DEFAULT NULL,
  `attachments` text,
  `is_deleted_by_sender` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sender_id` (`sender_id`),
  CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`sender_id`) REFERENCES `utilisateurs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES (2,2,'Remerciements','J\'acquise de reception','2025-05-22 18:39:22','[{\"name\": \"TC_8201.JPG\", \"path\": \"static/uploads/messages/TC_8201.JPG\", \"size\": 45474}]',NULL),(4,1,'Information','Suivez Mes conseils mes amis','2025-05-23 10:18:42','[{\"name\": \"TC_8201.JPG\", \"path\": \"static/uploads/messages/TC_8201.JPG\", \"size\": 45474}]',1),(5,1,'Histoire d\'innovation','Fleury courage','2025-05-23 10:24:36','[{\"name\": \"TC_8201.JPG\", \"path\": \"static/uploads/messages/TC_8201.JPG\", \"size\": 45474}]',1),(6,1,'Histoire d\'innovation','gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg','2025-05-23 10:31:36','[{\"name\": \"TC_8201.JPG\", \"path\": \"app/static/uploads/messages/TC_8201.JPG\", \"size\": 45474}]',0),(7,1,'Grande Innovation','Bon Bon','2025-05-23 11:04:15','[{\"name\": \"TC_8201.JPG\", \"path\": \"/home/fleury/projets/OpenISTA/app/static/uploads/messages/TC_8201.JPG\", \"size\": 45474}]',0),(8,1,'gggg','gggggggggggggggggggggg','2025-05-23 11:56:23','[{\"name\": \"BUREAU_DE_LA_COMMUNE_UNIVERSITAIRE.pdf\", \"path\": \"/home/fleury/projets/OpenISTA/app/static/uploads/messages/BUREAU_DE_LA_COMMUNE_UNIVERSITAIRE.pdf\", \"size\": 143742}]',0),(9,5,'Fleury','je suis sur votre platteforme','2025-05-23 12:38:45','[{\"name\": \"TC_8201.JPG\", \"size\": 45474}]',0),(10,1,'Reuissite','mon ami','2025-05-23 13:06:40',NULL,0),(11,1,'Reuissite','mon ami','2025-05-23 13:07:02',NULL,0),(12,1,'gggggggggggggggggggg','ggggggggggggggggggggggg','2025-05-23 13:09:10',NULL,0),(13,1,'gggggggggggggggggggg','ggggggggggggggggggggggg','2025-05-23 13:09:50',NULL,0),(14,1,'(sans objet)','bon','2025-05-24 18:22:00','[{\"name\": \"Administration-systeme-partie-1.pdf\", \"size\": 219658}]',0),(15,7,'Presence','Je suis maintenant actif','2025-05-24 18:42:33','[{\"name\": \"TC_8201.JPG\", \"size\": 45474}]',0);
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `professeur`
--

DROP TABLE IF EXISTS `professeur`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `professeur` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(50) NOT NULL,
  `prenom` varchar(50) NOT NULL,
  `avatar` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `professeur`
--

LOCK TABLES `professeur` WRITE;
/*!40000 ALTER TABLE `professeur` DISABLE KEYS */;
INSERT INTO `professeur` VALUES (1,'KARIMUMURYANGO','Menedore','prof1.jpg'),(2,'NIYONSABA','Therence','prof2.jpg'),(3,'MVUYEKURE ','Mathieu','prof3.jpg');
/*!40000 ALTER TABLE `professeur` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ressource`
--

DROP TABLE IF EXISTS `ressource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ressource` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `type` varchar(20) DEFAULT NULL,
  `taille` varchar(20) DEFAULT NULL,
  `chemin` varchar(200) NOT NULL,
  `date_ajout` datetime DEFAULT NULL,
  `cours_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cours_id` (`cours_id`),
  CONSTRAINT `ressource_ibfk_1` FOREIGN KEY (`cours_id`) REFERENCES `cours` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ressource`
--

LOCK TABLES `ressource` WRITE;
/*!40000 ALTER TABLE `ressource` DISABLE KEYS */;
/*!40000 ALTER TABLE `ressource` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tuyau`
--

DROP TABLE IF EXISTS `tuyau`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tuyau` (
  `id` int NOT NULL AUTO_INCREMENT,
  `titre` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `matiere` varchar(100) NOT NULL,
  `cycle` varchar(20) DEFAULT NULL,
  `niveau` int DEFAULT NULL,
  `departement` varchar(50) DEFAULT NULL,
  `semestre` int DEFAULT NULL,
  `annee_academique` varchar(20) NOT NULL,
  `type_fichier` varchar(20) DEFAULT NULL,
  `fichier` varchar(200) DEFAULT NULL,
  `date_ajout` datetime DEFAULT NULL,
  `utilisateur_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `utilisateur_id` (`utilisateur_id`),
  CONSTRAINT `tuyau_ibfk_1` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateurs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tuyau`
--

LOCK TABLES `tuyau` WRITE;
/*!40000 ALTER TABLE `tuyau` DISABLE KEYS */;
INSERT INTO `tuyau` VALUES (1,'Examens corrigés - Actuariat 1ère année','Collection d\'examens corrigés en actuariat pour la 1ère année avec solutions détaillées.','Mathématiques Financières','bac',1,'actuariat',1,'2022-2023','pdf','exam_actuariat1_2023.pdf','2025-05-21 19:58:24',1),(2,'Astuces pour l\'examen de Statistique','Conseils et méthodes pour réussir l\'examen de statistique descriptive.','Statistique Descriptive','bac',2,'genie',2,'2021-2022','docx','astuces_stat.docx','2025-05-21 19:58:24',1),(3,'Examen de Génie Logiciel','tres bon cours','informatique','master',4,'genie',1,'2024-2025','docx','1_1747891262.751394_Analyse_Bivariee_et_Multivariee_avec_Pandas.docx','2025-05-22 05:21:03',1);
/*!40000 ALTER TABLE `tuyau` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `utilisateurs`
--

DROP TABLE IF EXISTS `utilisateurs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `utilisateurs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(120) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password_hash` varchar(200) NOT NULL,
  `prenom` varchar(50) NOT NULL,
  `nom` varchar(50) NOT NULL,
  `role` varchar(50) NOT NULL,
  `avatar` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `is_confirmed` tinyint(1) DEFAULT NULL,
  `date_creation` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_utilisateurs_email` (`email`),
  UNIQUE KEY `ix_utilisateurs_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `utilisateurs`
--

LOCK TABLES `utilisateurs` WRITE;
/*!40000 ALTER TABLE `utilisateurs` DISABLE KEYS */;
INSERT INTO `utilisateurs` VALUES (1,'admin','adminopenista@gmail.com','pbkdf2:sha256:1000000$3RL97Agjjx1QVh8c$b0299eb9ee56c01c312b857f0ff3ef918fd68a8decfb1de4cbb131df34a61e97','Fleury','NIYOKWIZERA','administrateur','user_1_1747857219.jpg','2025-05-21 21:42:52','2025-05-25 17:30:51','2025-05-25 17:30:52',1,NULL,NULL,NULL),(2,'Cherissa01','niyonkurucherissa@gmail.com','pbkdf2:sha256:1000000$A7ZnhMixNeZbjVEJ$061f63a329d2ee323bc97df5d6a3dbae7d653f6928219b57d89b2b066f6113f2','Cherissa','NIYONKURU','administrateur','user_2_1747857272.jpg','2025-05-21 21:44:55','2025-05-24 19:10:04','2025-05-24 19:07:01',1,NULL,NULL,NULL),(3,'Tantine01','menedorekari@ista.ma','pbkdf2:sha256:1000000$oqSpu74i3pNQbo5c$401638362c6ee7e0b3eecd90471f452870ede3725a006d942989c0ddcc5d4640','Menedore','KARIMUMURYANGO','professeur',NULL,'2025-05-22 07:30:18','2025-05-22 07:30:18',NULL,1,NULL,NULL,NULL),(5,'Tantine011','menedorekarii@gmail.com','pbkdf2:sha256:1000000$sS23p4bBN8Kyo8Au$9c4c18d350df0869a265d5cd9d63b85441ba180bde616834be144e0e77db518b','Menedore','KARIMUMURYANGO','professeur',NULL,'2025-05-23 14:37:18','2025-05-23 14:37:46','2025-05-23 14:37:46',1,NULL,NULL,NULL),(6,'fifi01','fidianiyomukiza@ista.ma','pbkdf2:sha256:1000000$zDwj29M7aKuwHtBn$5d89bd1f5567a0c95c7c53b0bed3a8356ffda7e2f06bf05b8ab94bcc586bf36f','Fidia','NIYOMUKIZA','etudiant',NULL,'2025-05-24 15:57:55','2025-05-24 15:58:31',NULL,1,NULL,0,'2025-05-24 13:57:55'),(7,'jimmy0','jimmy@ista.ma','pbkdf2:sha256:1000000$yAxg9JVPSfaQvyAM$a1ae0ffcc2721df485fdf61cd2365b72203b8f8633e80c60076800cf958893b6','Jimmy','BIMENYIMANA','etudiant',NULL,'2025-05-24 20:39:02','2025-05-24 20:39:45','2025-05-24 20:39:45',1,NULL,0,'2025-05-24 18:39:02');
/*!40000 ALTER TABLE `utilisateurs` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-25 21:24:04
