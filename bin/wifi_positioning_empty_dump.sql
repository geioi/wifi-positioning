-- MySQL dump 10.13  Distrib 8.0.23, for Linux (x86_64)
--
-- Host: localhost    Database: wifi_positioning_initial
-- ------------------------------------------------------
-- Server version	8.0.23-0ubuntu0.20.04.1

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
-- Table structure for table `access_point`
--

DROP TABLE IF EXISTS `access_point`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `access_point` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bssid` varchar(100) NOT NULL,
  `ssid` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `access_point`
--

LOCK TABLES `access_point` WRITE;
/*!40000 ALTER TABLE `access_point` DISABLE KEYS */;
/*!40000 ALTER TABLE `access_point` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `place`
--

DROP TABLE IF EXISTS `place`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `place` (
  `id` int NOT NULL AUTO_INCREMENT,
  `location` varchar(500) NOT NULL,
  `floor` int NOT NULL,
  `access_point_id` int NOT NULL,
  `signal_str_min` int NOT NULL,
  `signal_str_max` int NOT NULL,
  `building` varchar(500) DEFAULT 'delta',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `place`
--

LOCK TABLES `place` WRITE;
/*!40000 ALTER TABLE `place` DISABLE KEYS */;
/*!40000 ALTER TABLE `place` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `place_detail`
--

DROP TABLE IF EXISTS `place_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `place_detail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `place_id` int NOT NULL,
  `detailed_location` varchar(500) NOT NULL,
  `access_point_id` int NOT NULL,
  `signal_str_min` int NOT NULL,
  `signal_str_max` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `place_detail`
--

LOCK TABLES `place_detail` WRITE;
/*!40000 ALTER TABLE `place_detail` DISABLE KEYS */;
/*!40000 ALTER TABLE `place_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `place_detail_without_adapter`
--

DROP TABLE IF EXISTS `place_detail_without_adapter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `place_detail_without_adapter` (
  `id` int NOT NULL AUTO_INCREMENT,
  `place_id` int NOT NULL,
  `detailed_location` varchar(500) NOT NULL,
  `access_point_id` int NOT NULL,
  `signal_str_min` int NOT NULL,
  `signal_str_max` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `place_detail_without_adapter`
--

LOCK TABLES `place_detail_without_adapter` WRITE;
/*!40000 ALTER TABLE `place_detail_without_adapter` DISABLE KEYS */;
/*!40000 ALTER TABLE `place_detail_without_adapter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `place_without_adapter`
--

DROP TABLE IF EXISTS `place_without_adapter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `place_without_adapter` (
  `id` int NOT NULL AUTO_INCREMENT,
  `location` varchar(500) NOT NULL,
  `floor` int NOT NULL,
  `access_point_id` int NOT NULL,
  `signal_str_min` int NOT NULL,
  `signal_str_max` int NOT NULL,
  `building` varchar(500) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `place_without_adapter`
--

LOCK TABLES `place_without_adapter` WRITE;
/*!40000 ALTER TABLE `place_without_adapter` DISABLE KEYS */;
/*!40000 ALTER TABLE `place_without_adapter` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-02-05 23:30:05
