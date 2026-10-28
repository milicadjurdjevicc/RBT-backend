CREATE DATABASE  IF NOT EXISTS `rbt_backend_api` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `rbt_backend_api`;
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `budget`
--

LOCK TABLES `budget` WRITE;
/*!40000 ALTER TABLE `budget` DISABLE KEYS */;
INSERT INTO `budget` VALUES (5,5,2,888.00,2026),(6,9,5,1400.00,2026),(7,9,6,250.00,2026),(8,9,7,100.00,2026),(9,9,8,100.00,2026),(10,9,9,150.00,2026);
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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'sminka','#ED9ADC'),(2,'hrana','#ABCDEF'),(5,'Housing','#8B5CF6'),(6,'Utilities','#F59E0B'),(7,'Transport','#3B82F6'),(8,'Health','#10B981'),(9,'Entertainment','#EC4899'),(10,'Salary','#22C55E'),(11,'Freelance','#06B6D4');
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
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions`
--

LOCK TABLES `transactions` WRITE;
/*!40000 ALTER TABLE `transactions` DISABLE KEYS */;
INSERT INTO `transactions` VALUES (4,'expense',1200.00,'2026-10-01 00:00:00','October rent',5,'2026-10-28 07:37:40'),(5,'expense',145.75,'2026-10-03 00:00:00','Electricity bill',6,'2026-10-28 07:37:40'),(6,'expense',48.50,'2026-10-05 00:00:00','Transit pass',7,'2026-10-28 07:37:40'),(7,'expense',32.00,'2026-10-07 00:00:00','Pharmacy',8,'2026-10-28 07:37:40'),(8,'expense',27.00,'2026-10-12 00:00:00','Cinema',9,'2026-10-28 07:37:40'),(9,'income',3200.00,'2026-10-01 00:00:00','October salary',10,'2026-10-28 07:37:40'),(10,'income',450.00,'2026-10-15 00:00:00','Design project',11,'2026-10-28 07:37:40'),(11,'expense',18.25,'2026-10-08 00:00:00','Coffee and pastry',2,'2026-10-28 08:23:46'),(12,'expense',76.40,'2026-10-09 00:00:00','Skincare cleanser',1,'2026-10-28 08:23:46'),(13,'expense',64.00,'2026-10-11 00:00:00','Taxi ride',7,'2026-10-28 08:23:46'),(14,'expense',89.90,'2026-10-14 00:00:00','Water bill',6,'2026-10-28 08:23:46'),(15,'expense',19.50,'2026-10-20 00:00:00','Music subscription',9,'2026-10-28 08:23:46'),(16,'income',2850.00,'2026-10-22 00:00:00','Consulting payment',11,'2026-10-28 08:23:46'),(17,'income',3100.00,'2026-10-25 00:00:00','November salary',10,'2026-10-28 08:23:46'),(25,'expense',16.20,'2026-10-01 00:00:00','Bus ticket',7,'2026-10-28 08:26:26'),(26,'expense',23.80,'2026-10-19 00:00:00','Lunch with coworkers',2,'2026-10-28 08:26:26'),(27,'income',125.00,'2026-10-26 00:00:00','Marketplace sale',11,'2026-10-28 08:26:26');
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

-- Dump completed on 2026-10-28  9:38:12
