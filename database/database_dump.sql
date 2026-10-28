-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: rbt_backend_api
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `budget`
--

DROP TABLE IF EXISTS `budget`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `budget` (
  `id` int NOT NULL AUTO_INCREMENT,
  `month` int NOT NULL,
  `category` int NOT NULL,
  `amount` decimal(9,2) NOT NULL,
  `year` int NOT NULL DEFAULT (year(curdate())),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `budget`
--

LOCK TABLES `budget` WRITE;
/*!40000 ALTER TABLE `budget` DISABLE KEYS */;
INSERT INTO `budget` VALUES (11,0,13,1200.00,2026),(12,0,12,350.00,2026),(13,0,14,120.00,2026),(14,3,13,1200.00,2026),(15,3,12,400.00,2026),(16,3,15,180.00,2026),(17,6,13,1250.00,2026),(18,6,12,450.00,2026),(19,6,14,150.00,2026),(20,9,13,1300.00,2026),(21,9,12,500.00,2026),(22,9,15,220.00,2026);
/*!40000 ALTER TABLE `budget` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `color` char(7) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (12,'Food','#F59E0B'),(13,'Housing','#8B5CF6'),(14,'Transport','#3B82F6'),(15,'Utilities','#10B981'),(16,'Salary','#22C55E'),(17,'Freelance','#06B6D4');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` enum('income','expense') NOT NULL,
  `amount` decimal(9,2) NOT NULL,
  `date` datetime NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `category` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions`
--

LOCK TABLES `transactions` WRITE;
/*!40000 ALTER TABLE `transactions` DISABLE KEYS */;
INSERT INTO `transactions` VALUES (28,'income',3200.00,'2026-01-03 00:00:00','January salary',16,'2026-10-28 18:37:55'),(29,'expense',1150.00,'2026-01-05 00:00:00','January rent',13,'2026-10-28 18:37:55'),(30,'expense',185.40,'2026-01-12 00:00:00','Groceries',12,'2026-10-28 18:37:55'),(31,'expense',42.80,'2026-01-18 00:00:00','Bus pass',14,'2026-10-28 18:37:55'),(32,'income',650.00,'2026-04-04 00:00:00','Spring freelance project',17,'2026-10-28 18:37:55'),(33,'expense',1200.00,'2026-04-05 00:00:00','April rent',13,'2026-10-28 18:37:55'),(34,'expense',240.75,'2026-04-14 00:00:00','April groceries',12,'2026-10-28 18:37:55'),(35,'expense',96.20,'2026-04-22 00:00:00','Electricity',15,'2026-10-28 18:37:55'),(36,'income',3300.00,'2026-07-02 00:00:00','July salary',16,'2026-10-28 18:37:55'),(37,'expense',1225.00,'2026-07-05 00:00:00','July rent',13,'2026-10-28 18:37:55'),(38,'expense',310.10,'2026-07-11 00:00:00','Summer groceries',12,'2026-10-28 18:37:55'),(39,'expense',78.50,'2026-07-19 00:00:00','Train tickets',14,'2026-10-28 18:37:55'),(40,'income',3400.00,'2026-10-01 00:00:00','October salary',16,'2026-10-28 18:37:55'),(41,'income',900.00,'2026-10-09 00:00:00','Autumn freelance project',17,'2026-10-28 18:37:55'),(42,'expense',1280.00,'2026-10-03 00:00:00','October rent',13,'2026-10-28 18:37:55'),(43,'expense',365.90,'2026-10-13 00:00:00','October groceries',12,'2026-10-28 18:37:55'),(44,'expense',145.60,'2026-10-20 00:00:00','Water and power',15,'2026-10-28 18:37:55');
/*!40000 ALTER TABLE `transactions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-28 19:04:53
