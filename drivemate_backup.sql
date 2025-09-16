-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: drivemate
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('429673ea7978');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `file`
--

DROP TABLE IF EXISTS `file`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `file` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `folder_id` int(11) DEFAULT NULL,
  `filename` varchar(255) NOT NULL,
  `path` varchar(512) NOT NULL,
  `size` bigint(20) NOT NULL,
  `mime_type` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `encrypted_key` varchar(255) DEFAULT NULL,
  `thumbnail_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `path` (`path`),
  KEY `folder_id` (`folder_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `file_ibfk_1` FOREIGN KEY (`folder_id`) REFERENCES `folder` (`id`),
  CONSTRAINT `file_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=388 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `file`
--

LOCK TABLES `file` WRITE;
/*!40000 ALTER TABLE `file` DISABLE KEYS */;
INSERT INTO `file` VALUES (275,3,4,'IMG_9323.jpeg','uploads\\IMG_9323.jpeg',2377700,'image/jpeg','2025-09-14 13:26:36','gAAAAABoxsKMDhCj08ZjD6ozNDfgSo6zI3deSdS5gOw36l5z8b2YV0vPunZECgiwB8JF4lOYQCwkx82yzqD6IYy3M4L23RN0ywV-vXyoPbG4EMRX6YP_QkmmBCdoj4aNuM0VUQ-XYO1m','thumb_IMG_9323.jpg'),(276,3,4,'IMG_9322.jpeg','uploads\\IMG_9322.jpeg',2371320,'image/jpeg','2025-09-14 13:26:37','gAAAAABoxsKNYNFDWY0fUq7sq52s6SuNU6ZZvBl82R9E3QSRscImwGbCuupBAVfBZVfbCGtpyxhLRv9_Z9bDe3cCxeAuL-nDjJiDE6zCx4Yy7zKLeba6JVMqZbR9qozYyLJIukwUl_1H','thumb_IMG_9322.jpg'),(277,3,4,'IMG_9321.jpeg','uploads\\IMG_9321.jpeg',2491236,'image/jpeg','2025-09-14 13:26:37','gAAAAABoxsKNBao4geqwFHzRWb75gi-ORmlACIlqZzQ9ABuA7s79erYTrf4nLTorQm3csYpDEAs0BGyyJ5iW8IOi2lEGkkzXbkxxZHaQmxLTPhjEVCeKFxWdmu3BVzx8hebFvOWpRIUM','thumb_IMG_9321.jpg'),(278,3,4,'IMG_9320.jpeg','uploads\\IMG_9320.jpeg',2284536,'image/jpeg','2025-09-14 13:26:38','gAAAAABoxsKOV3q3hCxD86a-Maj_AIc5FyBBODE9udttbGRpnqBbyYAqnk6X_Znl8BFbYGpg2kfvQUijI6H9N3jgjINLpAVEzltaLrpDKxXc9HjP9k-QGq7F6Cm2SlOh50TsFirT1xaI','thumb_IMG_9320.jpg'),(279,3,4,'IMG_9319.mov','uploads\\IMG_9319.mov',18502948,'video/quicktime','2025-09-14 13:26:40','gAAAAABoxsKQ-4sigGsT9GFLJlUcqfzHE2EuxrttaZ_QL8IqpY34784puVNo5rpHIIyORo8XpjNQf1XxLDLLRUiZQrb-aYbaXg2jLKv9EGY4t0Ho2PiLXxXhcJVZ2XfxfBri3NyUK1U4','thumb_IMG_9319.jpg'),(280,3,4,'IMG_9318.mov','uploads\\IMG_9318.mov',43937100,'video/quicktime','2025-09-14 13:26:51','gAAAAABoxsKbcbzIJlll8f01r9ngVvRVYHdmPcgeMoeRb6BRnlR11xbtrfTe6AoEBm2pBhyXHj0ZaIs_ZSR9Wgy6i7UBksaFbh8SOnsbIJKi2blF3xxacwOzbbDYW3SD5E7lDkr6aYwf','thumb_IMG_9318.jpg'),(281,3,4,'IMG_9316.jpeg','uploads\\IMG_9316.jpeg',2492408,'image/jpeg','2025-09-14 13:26:51','gAAAAABoxsKbsXm-ROByZmmivCF-ZYGEh4jD8sYBOfbh36h7lKqZKbgXFpFuTpqnCpAz6YMren66bbFqBHN2xPb2JGSBhTM1zxR84TWGUuY-7f8UE9r1mjTNNyrjVFy25PHMuecpsuW-','thumb_IMG_9316.jpg'),(282,3,4,'IMG_9315.jpeg','uploads\\IMG_9315.jpeg',2506040,'image/jpeg','2025-09-14 13:26:52','gAAAAABoxsKcyopooOwpFJV_RFxb3uJy-7TjVGVgaqQzg6A3JNQiLoduUpIePSuSHP-W_ruQOKs-U3N_Og5X8Q4qC7mGJlXKJsyFCt6_Q0RZ8x1f50a_LDE8t3u851QZeBNc-yIzgdml','thumb_IMG_9315.jpg'),(283,3,4,'IMG_9314.mov','uploads\\IMG_9314.mov',14174756,'video/quicktime','2025-09-14 13:26:53','gAAAAABoxsKdl-yG_Z0y7EUasZ648Al8i9DVrTD6OvkOZCXZ_eQXj7PeHipihe3zKFnyo9TfYH8VG5R4GeA5OVP5aDRIilzS6frbBBJ5qJCv9NqZvcL6dW1U2sCkHs0lArC_AZUeBmtL','thumb_IMG_9314.jpg'),(284,3,4,'IMG_9313.mov','uploads\\IMG_9313.mov',82389880,'video/quicktime','2025-09-14 13:27:10','gAAAAABoxsKub-g8I7T2mQQWcPBHTWhLZUMeHKNT20O_QZN_RJALadNMuDDQXbYmpYi1CYLvvW0i8uscJR7AU6RzrT4izGf9vZ4-er7Sh8HJLL2OC7UQi6XMnkmYMv8WPK8Rj_uGJgjU','thumb_IMG_9313.jpg'),(285,3,4,'IMG_9312.jpeg','uploads\\IMG_9312.jpeg',2937956,'image/jpeg','2025-09-14 13:27:11','gAAAAABoxsKv08d1DlXT4Chdnkj5letyhHEphEnqov0wY_5gwhd8BtgTS7he90g7ZAPq7Zk2Er1KtGJOBvGTRW-w7CdQrTySjaWBFYzqOGZwX5nwCqFf8d6nFLxgKqwylA73zmfMbuXc','thumb_IMG_9312.jpg'),(286,3,4,'IMG_9311.jpeg','uploads\\IMG_9311.jpeg',2965900,'image/jpeg','2025-09-14 13:27:13','gAAAAABoxsKxJF9XPV_Oanti4O9H2s7ncV10eb_fXfGZga3Uh_0lIMuy-RXVjd0evCvNTRyy7kovfowj3sxQV_vuDo3lSJCJiCf6ivD2_874RVa6-R8KcOavP6J0q0HEHQpO5fpFDs5M','thumb_IMG_9311.jpg'),(287,3,4,'IMG_9310.jpeg','uploads\\IMG_9310.jpeg',2957260,'image/jpeg','2025-09-14 13:27:14','gAAAAABoxsKy13GpS3Rvj478LlIHy32_DPb_Pbmvt1FVjMShZx_5LYw3CBDy3bxI7LGyXQiBvHPM6_vmWHStKTCAozq0DaDnPNfh3g7foNQGi4-4eD4GK9KhN4Xnoi164o_pGLS7l31h','thumb_IMG_9310.jpg'),(288,3,4,'IMG_9309.jpeg','uploads\\IMG_9309.jpeg',1036516,'image/jpeg','2025-09-14 13:27:14','gAAAAABoxsKymsl1roKMzoM7mJ_F_01IIQHGGdG_4GOVQZUgfIgsILqbSzCXWLXAjBDxg7YfufUW8D8cpDUtITgS7oHujNADqYgpcq4rudyS1quGk_SnRydqzrSrJU33DW3W-PhENLJ5','thumb_IMG_9309.jpg'),(289,3,4,'IMG_9308.jpeg','uploads\\IMG_9308.jpeg',2302860,'image/jpeg','2025-09-14 13:27:15','gAAAAABoxsKz6vQ1AAMvh5cTJMCwncPnFzp172iX_2OdU8fNtwO3bdSyO9DarfiMuUCBYPMPmG_HVei2wS01K5TXrxJqvO3CwOaVCM_rETGHajvsuG7Z2oMTWJUoH2L4epbCRm-P7hIa','thumb_IMG_9308.jpg'),(290,3,4,'IMG_9297.jpeg','uploads\\IMG_9297.jpeg',4704120,'image/jpeg','2025-09-14 13:27:16','gAAAAABoxsK0SCGpXXfA1QUbohhjKJJ4_5FOqzOutzAL72IcQ9xYNwXR34N7ldETlJ1GpNXukf6sO2KaJCmI49vHgWJS4u8t0Dyr5pnH2Mysg-ZjgTde0eIPL3d2QG4AJ7f5ZOHGLScX','thumb_IMG_9297.jpg'),(291,3,4,'IMG_9278.jpeg','uploads\\IMG_9278.jpeg',2459916,'image/jpeg','2025-09-14 13:27:16','gAAAAABoxsK0VGsm64YAiqzmZ7gRNQV0vyG60QTETPX1ViJOyNn6ThZ58jh4R9ZhXPvVlbBsS6oAu2pZLTNlCCZjy461eUa7_Rc7FlVkBHPIQs3XiapOCJEiXi2anP0x4YN6KRX288_J','thumb_IMG_9278.jpg'),(292,3,4,'IMG_9277.jpeg','uploads\\IMG_9277.jpeg',3487608,'image/jpeg','2025-09-14 13:27:17','gAAAAABoxsK1a8MFmGOu5j1ZfmdATv87O10wgkIt5SifWrYEn-d36aMoH7WAjTOx0cVPiOEEA5dkUmjqHVIZH9ds3ZRIrrNX4f1AodNK3jxnqrVmIWGy7rmDUd5Y8adGoozbc9tFWPj3','thumb_IMG_9277.jpg'),(293,3,4,'IMG_9275.jpeg','uploads\\IMG_9275.jpeg',3248908,'image/jpeg','2025-09-14 13:27:18','gAAAAABoxsK2huuk1WpdjjWxLH8XxigJ9GIQy_G8-UzOTUqzUA7JG-PshJKLBZ39qjghEWSnWdSklICZ44FjNyimY4kNW_GA3Y1auQLvwMgr5Hg47woviUWp5huHssuARcA83Y-XPLMo','thumb_IMG_9275.jpg'),(294,3,4,'IMG_9274.jpeg','uploads\\IMG_9274.jpeg',3489676,'image/jpeg','2025-09-14 13:27:20','gAAAAABoxsK4_40V1VW_y32elAirrUj1-DMyr_veveiYDZoq8U-1colaP46nGJEllkhCE0-Z0oVPY7Ezj3zlQGSb5ZWlJzsjw2ymwXZHUp1RWP0Ob4cwes_cvtz8mlgG_yEe4DxZxosa','thumb_IMG_9274.jpg'),(295,3,4,'IMG_9273.jpeg','uploads\\IMG_9273.jpeg',3443960,'image/jpeg','2025-09-14 13:28:39','gAAAAABoxsMHV8juZlye2l6Wbwr-A58uautv-yR5rMWKGLsvU4kWG4p3_04x6j6EBQyLyyxFyJT_G-MThjrvm-dVHQm7Tz0bRGEb0-10YaNoArl_WlX-KgacHtYvbPZzG5_4V72FvUoR','thumb_IMG_9273.jpg'),(296,3,4,'IMG_9272.jpeg','uploads\\IMG_9272.jpeg',3103012,'image/jpeg','2025-09-14 13:28:39','gAAAAABoxsMH2BkHdn7lYuTn9lHGy6Gb0kfpMkCNdy0-qA0ehG-2n_xoddMUmnyGt8hDXhMyus15QXIv25qzK0o0mOpxEyBWFCPW70AsRl0qNDHbNvyCnvgcwOjr6SW4LIGQyIWoD47D','thumb_IMG_9272.jpg'),(297,3,4,'IMG_9271.jpeg','uploads\\IMG_9271.jpeg',3561868,'image/jpeg','2025-09-14 13:28:40','gAAAAABoxsMIE2MXgvbv6e-pj2ulpXwEX3oA1b0C06L0i8GH0_tbrFjx3wFVNwkiN4hiyxrdoZWewtw8kFcGgI8Invr1e8-vQyz8SrbiFs2UfnlVJPSvKhuTmuD9oByQ6jdoXtGMmRZR','thumb_IMG_9271.jpg'),(298,3,4,'IMG_9270.jpeg','uploads\\IMG_9270.jpeg',2962680,'image/jpeg','2025-09-14 13:28:40','gAAAAABoxsMIR-L5qD_dVh9tZESvPExOX063pY8J7kBJWIrxNs9n_wmmlp_LMTkAgO2kfDqWnJaC7gEef6FctnnbZDtyhrZbmRg3DV5VP7i_oKuzHlxrGWgcior7yQMeZkWYvEOJf10K','thumb_IMG_9270.jpg'),(299,3,4,'IMG_9269.jpeg','uploads\\IMG_9269.jpeg',2973112,'image/jpeg','2025-09-14 13:28:41','gAAAAABoxsMJctxNCP_1WO56qhuyKHm8mvg1kojJb9FME--oEgHuetVENcOuDcSZ_JQKACe1UPhnWMmONt4jnV6MR-MNDYDuDUQOBp5B2hXQBNjI9qzWVoYG1wpjtAEY9vatGhB_iyXP','thumb_IMG_9269.jpg'),(300,3,4,'IMG_9268.jpeg','uploads\\IMG_9268.jpeg',2895564,'image/jpeg','2025-09-14 13:28:41','gAAAAABoxsMJkb0piAjDQLeZy3F3inewTQvpa-tSuPmqBw7yEce1Gs6Js4pSmu57VJYeWFTKIYA2b5x9nM4SfdeZeegjdjlNiGgNUf_G8UdTYnb6nIyYcSgAzVeXjgB8v7BMN0nlVe7P','thumb_IMG_9268.jpg'),(301,3,4,'IMG_9267.jpeg','uploads\\IMG_9267.jpeg',2777548,'image/jpeg','2025-09-14 13:28:42','gAAAAABoxsMKUBX10qO9h-NwT4_NgHgazmF8lzD8ehlSTuH0HaiY0xDWB2CbIzhlTQjN0GNPfGW3DzWiiBSs8JOdDb9FpltFN4zcg-ulAdU473lPUnkz0PqFy1Cgy_60IFzz816O_jgo','thumb_IMG_9267.jpg'),(302,3,4,'IMG_9266.jpeg','uploads\\IMG_9266.jpeg',3536996,'image/jpeg','2025-09-14 13:28:42','gAAAAABoxsMK9V6WyqoIuNSVRgoifqOOO5jyxBxpd7S4dcxw-C0781Hnb80mvAmesIbOmVVk2zGlNFNWq8TW-hGY5H_DP70K8FpjZG5E8R5KUKfztb8rzU9ij1y_Sm4ZKhVkNe4nMjds','thumb_IMG_9266.jpg'),(303,3,4,'IMG_9154.jpeg','uploads\\IMG_9154.jpeg',4274212,'image/jpeg','2025-09-14 13:31:21','gAAAAABoxsOpkAd0WMI9wf5-F_hGYuSzYjx2IwqqAbXA9X9ReClzvgeP9d7aqy6xRwdfokJHVczkQidbWTugZzhPwU6d1Rmk43kwiVvhzV55S96OBqf1B_qNDJL8zhz6d86F7V_RTM5t','thumb_IMG_9154.jpg'),(304,3,4,'IMG_9153.jpeg','uploads\\IMG_9153.jpeg',4169848,'image/jpeg','2025-09-14 13:31:21','gAAAAABoxsOpyqH4jFhXGlzT1gF6cvGjwxHDyLGt64-U7uCqFg8SVVAw7eosrkmg0LR3JNmKhJ80ZAwu6sw10xzpzy3ETTn2x4k8DGg9DA1TXfECMS0v9OoLd-JWOZ-B7mQRLL321wJM','thumb_IMG_9153.jpg'),(305,3,4,'IMG_9152.jpeg','uploads\\IMG_9152.jpeg',4205004,'image/jpeg','2025-09-14 13:31:22','gAAAAABoxsOqrXvhUnTKW1wqvLKC6aDZqr0WJrbqPND71dP5SY8MvgGpLqxag8DJ7b48bikHARhmUCcm4AAiZ9_4SFmQVSlzNtRkxdhQSNfhyvtZMkKYAbWH-XpQ6-tWjjh-xw_U1cBk','thumb_IMG_9152.jpg'),(306,3,4,'IMG_9151.jpeg','uploads\\IMG_9151.jpeg',4352036,'image/jpeg','2025-09-14 13:31:22','gAAAAABoxsOqox_ZwFqEhoePXMVU4PPnMLzcVBn4L1kXPrIcWj2ZeFQ0Ac2la0mJJEIHwdb2FxJBIYQmhBGvEbwFBXZ0_WDYDjTAkKiApTE0hv9e_cl3uQKhSb_O4KSRzlULq1B4SWke','thumb_IMG_9151.jpg'),(307,3,4,'IMG_9150.jpeg','uploads\\IMG_9150.jpeg',4251916,'image/jpeg','2025-09-14 13:31:23','gAAAAABoxsOr-N0x1dYwAMBil_43D6KKSA93f2eVAUY36xKlzQQPZA4I1zCuiQodFs2KPtmrq7YVvQCACST3rObDgPlPh9D1YSf5ke0y1PchnXEm-xMgXwc45CjfqwQ30mHcnE63kUYl','thumb_IMG_9150.jpg'),(308,3,4,'IMG_9149.jpeg','uploads\\IMG_9149.jpeg',4177464,'image/jpeg','2025-09-14 13:31:23','gAAAAABoxsOrK-t2WjM_uqp2CvSgaQEtwSKxw-Vn94LNLaMcL1ugzgwgDmRvjSChlSZZz5kh9DYHKEK35qIrtKDpCpQSnBauia1Yx4sIdGK40R-q4tGm6PzUkih4mNlWw0ARb3w-_mGR','thumb_IMG_9149.jpg'),(309,3,4,'IMG_9148.jpeg','uploads\\IMG_9148.jpeg',3569740,'image/jpeg','2025-09-14 13:31:24','gAAAAABoxsOsSXfWQ7wG5Gvt1Cytj45So-kqsp3Hvz0GHv_BYSX2ME8CYfKR9pn6xEcmcZI4VOHwuUsUc-V6qDIHqW4kKzBimN8qP5YWaIhz-ZwVhYWfzv0eMJ4Rscc2XhP4cSC2u4nd','thumb_IMG_9148.jpg'),(310,3,4,'IMG_9147.jpeg','uploads\\IMG_9147.jpeg',3478308,'image/jpeg','2025-09-14 13:31:24','gAAAAABoxsOstw2rpg8lkktZ0bObGIkrtvxSV4lRYgG2nV2jUP7R8jcFJ2VrLA6IcSYRtQTm9-7H5kbge9Ts4K5wb8YfyMWnK89r6Yn-MtfBJ5CmL9sy_d0VqL2DEGOWZxTqOt07BW6v','thumb_IMG_9147.jpg'),(311,3,4,'IMG_9146.jpeg','uploads\\IMG_9146.jpeg',3452620,'image/jpeg','2025-09-14 13:31:25','gAAAAABoxsOtZhzxvmrbVlnfCGlt_NwY-0DqSJ_kSua7s_Fk1IgfuJGyBaKFxwRVfjSY6LRvu1h0EgMhUa0vQbPGrDENIdnZJFCMj1ISyuQcr9jZpPjem3AMVknqw9XtHBVgzNI8lMcG','thumb_IMG_9146.jpg'),(312,3,4,'IMG_9145.jpeg','uploads\\IMG_9145.jpeg',3333240,'image/jpeg','2025-09-14 13:31:25','gAAAAABoxsOtFzjfrPA7u9LYYxiov5ByDflZNkwCVl-u2FbKW_P8hdoh_DjG6WTl_w8s7K_upPo0Zvi6QKq1GgFRZ2aEfcL_qz9JBQmQCAFAYTqpxx3Gc6shxNrkcKKhiUN6iDMwluHF','thumb_IMG_9145.jpg'),(313,3,4,'IMG_9144.jpeg','uploads\\IMG_9144.jpeg',3407884,'image/jpeg','2025-09-14 13:31:26','gAAAAABoxsOuaK2w12xIunOeIF-bQjYlA5YL6gloSSk7Oq36IvF_n4fWtrt-xBMWn5ua1rR1TgH7PyDSSAUPpsJHdcY3j-RbTDdEiSfhx20cDnknDVSUmM_CG0ekKtkhEnIxn2qwdRbu','thumb_IMG_9144.jpg'),(314,3,4,'IMG_9143.jpeg','uploads\\IMG_9143.jpeg',3330232,'image/jpeg','2025-09-14 13:31:26','gAAAAABoxsOuuG5rH8j2EptoAgzU-UK3CPyFS7krvvy-rNcAc8cGrk5eXGcTGeogTiAoTgPFb_qvKrv9_Y2M9gIcqClxhl0oNkKXP_GHr-QWKxzLIJ-_3nA8kMS5x2EKPUEDNP3emjq4','thumb_IMG_9143.jpg'),(315,3,4,'IMG_9142.jpeg','uploads\\IMG_9142.jpeg',3416332,'image/jpeg','2025-09-14 13:31:27','gAAAAABoxsOvzbTn8MziLofVKpau0tX-dadtv_7LlL4plpVQ7EUh2mA_bjPt-vsEWRMAwdW7iYEmukFO4GX39oEY5CKxdvP43NWVRHeo0Xg8eXgcpMTwr-w4eRWDf01i1ZH2vfucWUl6','thumb_IMG_9142.jpg'),(316,3,4,'IMG_9141.jpeg','uploads\\IMG_9141.jpeg',3401740,'image/jpeg','2025-09-14 13:31:27','gAAAAABoxsOvlTe-4ZQY7omW4SdWhhwz87xrEPLFMz8UdWO4WgVi3Dd4ee3OqUIHrJ2fzfhSDMHWaoUALLKAQ2PWK4RZoegxsDIP_w24QWrlEf9g_77KJF6ExlbPPQPtDJAVIZRRnJZa','thumb_IMG_9141.jpg'),(317,3,4,'IMG_9140.jpeg','uploads\\IMG_9140.jpeg',3798500,'image/jpeg','2025-09-14 13:31:28','gAAAAABoxsOw3ip54MMQz4cQMzbny56AjeqvJpeALypwvQbb4Tf4P4LDqnsu1NZYzMNTDa4drokWcm53EFqybugPOis7juLKsWV2YkWFwN0Gpv4APkM6uP8nxz9j-mrHHqyZeGqVXXBe','thumb_IMG_9140.jpg'),(318,3,4,'IMG_9139.jpeg','uploads\\IMG_9139.jpeg',3812452,'image/jpeg','2025-09-14 13:31:28','gAAAAABoxsOwJUTpSte0gEegOqNgc_cwjCcPDUZNGdyosMak2uf79_VcOg6eaBvJscDXcx5YpWU4OtIXlZlx59nDskrwMKDdhmH5HkMZcIoezXs6lh1H4O33rtOqNa6Ildhj6uQ_0057','thumb_IMG_9139.jpg'),(319,3,4,'IMG_9138.jpeg','uploads\\IMG_9138.jpeg',3395896,'image/jpeg','2025-09-14 13:31:29','gAAAAABoxsOxKvE1ZNLf6nRkMOYa4vV4cegezCog2HfqVH9EXfnGXxiR2KY-euzQFUTjD-IspOx0Inbhdc2Fh4VGIcieck3av3JxGjM39kIi8kgCmcx45wQxYVgBbr8c0Aj5cNJQaewi','thumb_IMG_9138.jpg'),(320,3,4,'IMG_9137.jpeg','uploads\\IMG_9137.jpeg',3408292,'image/jpeg','2025-09-14 13:31:29','gAAAAABoxsOxKYoD5GOSViZJaEIiWO_OmopsQ5TViMCriKT4jT9AA1AYistTY8dXPE7whD96RxRIXy-NlH2By1tigscfz8dc7I5L6F2LxoPZWrr7PUPLftM_XKfRH4XAvgN6_t5l13eF','thumb_IMG_9137.jpg'),(321,3,4,'IMG_9136.jpeg','uploads\\IMG_9136.jpeg',3185592,'image/jpeg','2025-09-14 13:31:30','gAAAAABoxsOyplmcEma-MKJ-fmSLejTjLoRfmgQP6sb1uCUS9i8xBhizHBSvMEc2qcbun2Dc_hyGIcx98kZBaFP44qvM9u61oAW4LFrttaczfuje18cYgg9KF6XM9-r2tbrDMzpwneLZ','thumb_IMG_9136.jpg'),(322,3,4,'IMG_9135.jpeg','uploads\\IMG_9135.jpeg',3926072,'image/jpeg','2025-09-14 13:31:30','gAAAAABoxsOyYCU1B4TmzG35rW2z8Ly9rzBpN6LJOqMQSgU4Xg4GDPAa4m4xwRwRrGpsjcwCmxAxMwmEClW4jo-O4npsCDlB8wbNrcQTe90D8H1fF3ToALEIjzGHj_TtKrbu8rQxPE3J','thumb_IMG_9135.jpg'),(323,3,4,'IMG_9134.jpeg','uploads\\IMG_9134.jpeg',3835404,'image/jpeg','2025-09-14 13:31:32','gAAAAABoxsO0jZIppSR87d6aTcPHTw-f3rAD1c3xc4Icx6BOS9vJgXzOSXB3ygWkv0Cpq1S-AKMwsQxfPGLA40SedaMG1z1E8PkdXQrUu6iZAd5a64xauU6JFLh4eaNIYIZziZ1p-lSE','thumb_IMG_9134.jpg'),(324,3,4,'IMG_9133.jpeg','uploads\\IMG_9133.jpeg',3863524,'image/jpeg','2025-09-14 13:31:32','gAAAAABoxsO0FTHNmK0WcwRXGhJYVMtMmjk943wBdq4fxQwR4t60TrPkFjE1u6_plf9f14WIFhTe8NBJAahGyi7khDoKw5f6_fshW4diJLW7NAMucuDTdW4DU1OpMFhxEtTnl8os8bsV','thumb_IMG_9133.jpg'),(325,3,4,'IMG_9132.jpeg','uploads\\IMG_9132.jpeg',3802020,'image/jpeg','2025-09-14 13:31:33','gAAAAABoxsO1Ce90ps1_AcgE7gEWuDj5Qs3d1bJm71-DJJU4-nMg7nVaWTCWGCXnu63t-lMwxYA3e1g1HciOzn6J9p4YTfUX7l_B-r9_C6cSXtzwazAeiH9T5XPohLlpZfoIptO6vizJ','thumb_IMG_9132.jpg'),(326,3,4,'IMG_9124.jpeg','uploads\\IMG_9124.jpeg',4056100,'image/jpeg','2025-09-14 13:31:33','gAAAAABoxsO1PmndR6HHOps4ZjfiNXTQjL0oS3rBfFEkxkqo0O51vIGG1-FhDj04LpC1BGTRZ2V1wGfMxYPCiNeRcUOOVNvb4gP8Ezs3_V_beIfBBMcg2b4xbmY6f6DbiLp6wqDEmB-5','thumb_IMG_9124.jpg'),(327,3,4,'IMG_9122.jpeg','uploads\\IMG_9122.jpeg',3655948,'image/jpeg','2025-09-14 13:31:33','gAAAAABoxsO1tXHNdC9amrAssX1WU6juYVv3_0AcGfgW4OTBjgfb9SdoScrDVNT4HuJebPnyNMpYCfzEogyEMXl-HR4IZMaUAa93xUTih7OM4kO7nBHvb2HiHJ3ovIIA7EWTjl-XxP-U','thumb_IMG_9122.jpg'),(328,3,4,'IMG_9121.jpeg','uploads\\IMG_9121.jpeg',3813112,'image/jpeg','2025-09-14 13:31:34','gAAAAABoxsO2u35pTUVpnTA13YtGG4T-s8bWIwqlhqY2oP9HyC5hWppzlsmXcdprgbByYw3gRfFkWv5J4oqFpTYmEQz2iQ3cXli1k7I_ErEsbm0nh4VpAwYO9Jv6oE9LeEUFlkxjXkIb','thumb_IMG_9121.jpg'),(329,3,4,'IMG_9120.jpeg','uploads\\IMG_9120.jpeg',3771704,'image/jpeg','2025-09-14 13:31:34','gAAAAABoxsO2aG_lc8XPBCafM2zsdBPGCuJxqOcDV_qx_uKh0qEEAlv4vo7zxN9tIx0a-crEa5eNxcQMC_smanURdlA_YAVR78d7QVbPIUT8QHp22LQHnk-vPay5euZAs8ccEUx32xnV','thumb_IMG_9120.jpg'),(330,3,4,'IMG_9119.jpeg','uploads\\IMG_9119.jpeg',3690764,'image/jpeg','2025-09-14 13:31:35','gAAAAABoxsO3xtq7-zmJR4F39hFGWcj3IehcajhZuZNXjI2AXmWoxxJMOyRjPKVksIYdWgP8J1cykeEBkwmYguueH69UOqABMXl6ZO-kIdHQnsqK0K-3LDpKoEWoYX30gAhgnYD8Dws_','thumb_IMG_9119.jpg'),(331,3,4,'IMG_9118.jpeg','uploads\\IMG_9118.jpeg',4257336,'image/jpeg','2025-09-14 13:31:35','gAAAAABoxsO316vfmnUB__Z-90siFlyC0qRpfNmhSe-XS1QAPGjN3qKUrM6u_HoJKrMhfSkcVB54aDzawYSlKdjtUbmsTjEgSvD93tdTSSq6dQ4hq622Y4AyWwGc7iFyfkjH4B3COwxH','thumb_IMG_9118.jpg'),(332,3,4,'IMG_9117.jpeg','uploads\\IMG_9117.jpeg',4495972,'image/jpeg','2025-09-14 13:31:36','gAAAAABoxsO4uIWpaAqOShlhcybOmrfL9RDXHgy8juJgUDVSoLmN8Rfv-9DNDvxbypUvxEZtjAx5SAljdNnqxDLpXIxURsjDJZoDFuDH1n7wFNwbMgcYW5QAH5TaeQ1U4F23-87IAEf7','thumb_IMG_9117.jpg'),(333,3,4,'IMG_9116.jpeg','uploads\\IMG_9116.jpeg',4362340,'image/jpeg','2025-09-14 13:31:36','gAAAAABoxsO4r-ygLexNmNIxQCQxIj26x10TeBTGrEiTuDLiAAq-B7h41Z-xThxJ2l4tfceVya8YsTSDXdwcjIVhjmjA6GfN3SQhp-w9cZzXRiKIcpRSKucT6sRg63jIRdy0TiMZd_S-','thumb_IMG_9116.jpg'),(334,3,4,'IMG_8716.jpeg','uploads\\IMG_8716.jpeg',4078476,'image/jpeg','2025-09-14 13:39:39','gAAAAABoxsWbQtRcCIzVAUp3AgWThlwXrD8CRU6HGEPH66yJCv-yrJZ7hGRAauaJzBmFNNitNOWIg6LE0KHtg1LkdqDCk3bYOYQDnyhGRGk2fdavjqcZgJ0Z6jBLKfK5Fwb7OzmKEols','thumb_IMG_8716.jpg'),(335,3,4,'IMG_8715.jpeg','uploads\\IMG_8715.jpeg',3933132,'image/jpeg','2025-09-14 13:39:39','gAAAAABoxsWbQ8wJ4FucZCN_7f6V1l866JJ6rP57LLCJBGCX7SwF9c2mL5i6bMwKRsRBwfcTg7gCCRD0cY5BqO51I-g4DUi7nkpC1OD9ipb1tTYByidnwCXq63ibhsYUUD93-F6ZavwW','thumb_IMG_8715.jpg'),(336,3,4,'IMG_8714.jpeg','uploads\\IMG_8714.jpeg',3973432,'image/jpeg','2025-09-14 13:39:40','gAAAAABoxsWcN0N1fAW237QIRcinPND7FBmG6K6DKnaLUlA03WB3j5GlnzNwELsF-evwSH8U2DGg_pXKgHfx530DTAFL6w5iqZHNSdBwze3vlUDcUYDt-zuMu9YNqEBbnG4MO1EOa1ub','thumb_IMG_8714.jpg'),(337,3,4,'IMG_8713.jpeg','uploads\\IMG_8713.jpeg',3858872,'image/jpeg','2025-09-14 13:39:40','gAAAAABoxsWcpKrNDZpGBXYsWTDPUbMYR1hczwJSE7MKlwZho-_Apc0KEDm1WIY7sH0lmMeOl0fN3qyhxcC4SyUWsLlvcIuQfrUyqKt67X1nqK_q9bW2nSFJ88jt2yvtd5o9MQPvjqm0','thumb_IMG_8713.jpg'),(338,3,4,'IMG_8712.jpeg','uploads\\IMG_8712.jpeg',4054668,'image/jpeg','2025-09-14 13:39:41','gAAAAABoxsWd718NYloI6Q_6o2uYh6SeKhivnTBHDUhpFFHDcO-00wjjpvMgobFmNF3Qd6iRdgmMrH-dDhrgMlRzHER5k2nYn3hliZJfmUz1DlYgh4MCkrlQ3GahZnqWtY3EacoRTTjz','thumb_IMG_8712.jpg'),(339,3,4,'IMG_8711.jpeg','uploads\\IMG_8711.jpeg',3969420,'image/jpeg','2025-09-14 13:39:42','gAAAAABoxsWeMqyBTxXIHRXLJpiXGkG57Xjq9W3JcKVgOYLjU-6RxX-jctbC0lW5_vLZCutZOq551_Xg35768iOo6LrKZOX20cRUFWvnuYW1TerRt43zdz98qErw2MwBZRN8vwhjTSb2','thumb_IMG_8711.jpg'),(340,3,4,'IMG_8710.jpeg','uploads\\IMG_8710.jpeg',4079032,'image/jpeg','2025-09-14 13:39:42','gAAAAABoxsWelD0oVskX6gUiRM2TQZXzW25MsbdNnRv2hY0rn50IvN72Izbye2FOWW67zKs-ykQZlN8n4Zel2z1YPBJCJoH-NLg9CmEvctcTXLzfC5h2mb3Sg60NwP_htNCJKeTbQXNQ','thumb_IMG_8710.jpg'),(341,3,4,'IMG_8709.jpeg','uploads\\IMG_8709.jpeg',4059788,'image/jpeg','2025-09-14 13:39:43','gAAAAABoxsWf5kN8HpZKbrxiZOKhncTnISjdBhUFWQ4WAuUYoQZfgYZRO4Bqs-wD2LOVqnEna-WAFguuJv5ufhlra2Zf7tzEdqavB3pi4WD9osKjrVL6pkkPeWD1lNQuSLM8_O-Lwjua','thumb_IMG_8709.jpg'),(342,3,4,'IMG_8708.jpeg','uploads\\IMG_8708.jpeg',2654840,'image/jpeg','2025-09-14 13:39:43','gAAAAABoxsWfeure3bfVJOmkGe2If7T2fmswa96bay0HXipKHKQrlxflQ8tDdVqrU2zfiBpxQGhmaS-Eri5xRJFvtwjB6XSMFI4wM2H3mREqKEOQvPxqM3Le8FnvGQpFbvcPTJhXJ9jl','thumb_IMG_8708.jpg'),(343,3,4,'IMG_8707.jpeg','uploads\\IMG_8707.jpeg',2662648,'image/jpeg','2025-09-14 13:39:44','gAAAAABoxsWgKPVcYYaN9Ii9lmYmGa3-LNdsW0IV_PPcqvassrFGHyjJ4ce94ql4PRTguviR6btZzfQ-K5fWxvpa54SN-TDMDLsm4udGawgt8Q2myFd3ltl0DzMliBzbTDh0g5D_Tjjq','thumb_IMG_8707.jpg'),(344,3,4,'IMG_8706.jpeg','uploads\\IMG_8706.jpeg',2748940,'image/jpeg','2025-09-14 13:39:44','gAAAAABoxsWgOLvwIjI3iJXkCd6bNsxYNJKk7sIEtk1rDSIkojaxU3H6aNxhP_XbG1ClMRA-46f8NPcm8d27K8bGj3Gm_ykI7vnUzBC0Zi-tN1Db0TnLL9bc8O2eN84j7Z7GPWOD1sJ3','thumb_IMG_8706.jpg'),(345,3,4,'IMG_8705.jpeg','uploads\\IMG_8705.jpeg',2506444,'image/jpeg','2025-09-14 13:39:44','gAAAAABoxsWgK6EPnfMSmEqf2rqnWqQTtqO3PU1CesECkaDMAm2mK0Lios1DoGFZf2mK-MPj_LtnBAAFZYDNFZA4-kcc0X0DgDXHb2p7LzItkNEYmvSYKifO1_JcQ7FFmE_9EqVRy-4B','thumb_IMG_8705.jpg'),(346,3,4,'IMG_8702.jpeg','uploads\\IMG_8702.jpeg',3801764,'image/jpeg','2025-09-14 13:39:45','gAAAAABoxsWhcO_o8tesTflO7Eu4ft00KWf3rSaqLgBHEL-mJkbbAopZ-xZHWBOhPeUhW12VDwfgtJXil2hif6NoMAcHrZImHZ-OngD2AIl6IQnLlRR9kfxh65Ehn2Wm0Ph3o0GufeL7','thumb_IMG_8702.jpg'),(347,3,4,'IMG_8701.jpeg','uploads\\IMG_8701.jpeg',3953252,'image/jpeg','2025-09-14 13:39:46','gAAAAABoxsWiezZL2WbiTSRLThrWgNuz-5a_4R6ypkEGTLouBbFutyys8CZIFo6XR4RVp8VDVNAjD0GXCafTbcVSIzZa5lK9e8QNjo-VrtAHVyt_3fAeG75FKp-KZqGKO1Q-dGgSvpTR','thumb_IMG_8701.jpg'),(348,3,4,'IMG_8699.jpeg','uploads\\IMG_8699.jpeg',3693496,'image/jpeg','2025-09-14 13:39:46','gAAAAABoxsWieimjuhJNr-czrbpB8uQFli_hAAjELgxw07Dm-vgBJn4zBuH9_X4MoEWmTEuHccOpPWcfgtXo_A1sPVpPJ5KOjv1aB9i1z9Vp2aG3IOXEovIWDpqf8nTp0vOr5AQfXQEe','thumb_IMG_8699.jpg'),(349,3,4,'IMG_8698.jpeg','uploads\\IMG_8698.jpeg',3668068,'image/jpeg','2025-09-14 13:39:47','gAAAAABoxsWj320yV1DAIvOLYOLpsEXJs7NqZ9Bqd2Yrt3LCbQkjSyW7hCOULRF0dbCTPEVtFlF7n8J6RacHd-hld8pqkwHfe_BPr-9zc2pKvDUbOOQPUVPy5O81jAIwlLig0ZLdkhxB','thumb_IMG_8698.jpg'),(350,3,4,'IMG_8697.jpeg','uploads\\IMG_8697.jpeg',3757368,'image/jpeg','2025-09-14 13:39:47','gAAAAABoxsWjR0nScYe1b1fjBsUCsQEbv8St4805KWIE1RVuADKSCs9HPGi5mn-AyWcSHaT02-h9QT8ZKyQynW-sJVj1MqGXiJQJpzoR-a945A9mtUczh-dM6_kAEZuHtzFmWSS9haNV','thumb_IMG_8697.jpg'),(351,3,4,'IMG_8696.jpeg','uploads\\IMG_8696.jpeg',4047628,'image/jpeg','2025-09-14 13:39:48','gAAAAABoxsWkxXI3m1mNswBD778GBYUChFxrKwJt6wCWWkc7kN1-gUwBS4QfXz6PreVWKIfw7ivJPp5g3h9KITbHNL8u3aCL6xaAQsv6I9adY6ka7NEi4OZdOEOhVhwnVZpSMbUw30xw','thumb_IMG_8696.jpg'),(352,3,4,'IMG_8695.jpeg','uploads\\IMG_8695.jpeg',4036812,'image/jpeg','2025-09-14 13:39:48','gAAAAABoxsWkF6UN3Wyk_iRXcPzMq3FcHU4erTuKqjpDtONW-m9p4Y9WmX45l3H8KHQvwBpe-OZSPqoo-jGhNXL5sG3S2Ma1cFfnDCii5UN56o5JyhdRn__J0mkxfyuHYLZ1WlMXbi4u','thumb_IMG_8695.jpg'),(353,3,4,'IMG_8694.jpeg','uploads\\IMG_8694.jpeg',3944612,'image/jpeg','2025-09-14 13:39:49','gAAAAABoxsWlxBtbJTgqLeGgzidm4jcfOyB3F93LYe6adz2qqgEprDD0as-QoF4iteSbV_UIpotn5myE0mV40pyGIlYt9oU3z8OFyVtC2ZWFD3-ZlFtqdwM0ezdQ9f4OSxDqfXPCMIEH','thumb_IMG_8694.jpg'),(354,3,4,'IMG_8693.jpeg','uploads\\IMG_8693.jpeg',3888716,'image/jpeg','2025-09-14 13:39:49','gAAAAABoxsWl-1NqJ0fFThtf61UCQ0dcHRjZ6X-uCruOc29l6R-tPMhQv71K4UHY4mN79qqPXQlbRhhowQrOEgHUNiOO5CkvrW6mc2569U5C5iNprGihLvkeVcPoi8_e4hg5-_wHJqGF','thumb_IMG_8693.jpg'),(355,3,4,'IMG_8691.jpeg','uploads\\IMG_8691.jpeg',2505380,'image/jpeg','2025-09-14 13:39:49','gAAAAABoxsWlE0fPlelYqlYPpZ30w0pOU4scb08jUwhiZkYGdCCa1em9dQwc5AwLapybcccJ29tYjmLKj3B-mM6JsJEYxoeq6FdEo_EhVLyzqIvR-yPFicCnYtvDnzmNeeJOX2rRmgER','thumb_IMG_8691.jpg'),(356,3,4,'IMG_8690.jpeg','uploads\\IMG_8690.jpeg',2639052,'image/jpeg','2025-09-14 13:39:50','gAAAAABoxsWmPml1zlP_9YMh29WjliwnbtAMBLfN1ajBC1V-8CKT1L_dQHRMoWVt-lqwuGsEzw-slORrGlKmwZPIQ_rUvFDo1tCeAEWlUNINdh0AqI3rEsNTF4ssZK-k01SChRNbTJUM','thumb_IMG_8690.jpg'),(357,3,4,'IMG_8689.jpeg','uploads\\IMG_8689.jpeg',2579492,'image/jpeg','2025-09-14 13:39:50','gAAAAABoxsWmTUHsG-pXa6l3-do_C_PK1lcbep0bi5y5emQDDnWnTp512NbBBVKfxPoiDOw0U5bXlaSxNPCEBObiFDNdvwBKENZlDoPsc-2NXztKGAaE3ycRPZLN_lw_fD7OO1fMFJi3','thumb_IMG_8689.jpg'),(358,3,4,'IMG_8688.jpeg','uploads\\IMG_8688.jpeg',2589496,'image/jpeg','2025-09-14 13:39:51','gAAAAABoxsWnSG9d1jjOUJV7_dxK_AwkNl-naOn7yuK8vHS2NWCmhKisfqjyAZgybxTtJhbbSBiDTT2Ep9zzQ9si5yES13FqGVWgcZddby1yIIR5T_lLmqUEmfIttr7dZ1mu72jZ7tcY','thumb_IMG_8688.jpg'),(359,3,4,'IMG_8687.jpeg','uploads\\IMG_8687.jpeg',2558692,'image/jpeg','2025-09-14 13:39:51','gAAAAABoxsWnPE_M963NYu0-RwIuzJ9sLoD4xjYuNkyxnp7F14TQzXSix9cYO28LzH07XZM3ew6-H_NEW20Fti1LiBxPdWyY1JKsRWl8vo-JDPHRjiQAWN2X3W1ruEku7X6DGIdPdLBy','thumb_IMG_8687.jpg'),(360,3,4,'IMG_8686.jpeg','uploads\\IMG_8686.jpeg',2377996,'image/jpeg','2025-09-14 13:39:51','gAAAAABoxsWnB6jEDjk71YASZRaH9Gi9JIhJjlNMA8PfGQ2rKHpGCh6wLbS9oqRAqJkYGm6v0Q-oqOmtZJ7yjRNBVW81sfiUJYL-viIWpaPuToKq5vRBQQimoIqzjncMVTOf-firv1MF','thumb_IMG_8686.jpg'),(361,3,4,'IMG_8685.jpeg','uploads\\IMG_8685.jpeg',2207992,'image/jpeg','2025-09-14 13:39:52','gAAAAABoxsWopoBBvMNOMPsC0oWVgI55Ujflluq7Jrm___Uz2lFB89Y8EnsWEAPoeMYa_EvpqZAZmj_m_46qAbd5qU_rk2iNtWuWNVg7gzw7ldUsv0cKeXFt_8WGRNanasQTWAbGeiE0','thumb_IMG_8685.jpg'),(362,3,4,'IMG_8684.jpeg','uploads\\IMG_8684.jpeg',2703308,'image/jpeg','2025-09-14 13:39:52','gAAAAABoxsWoHhKE-2K60m3Rqph3T6SUVdk7P0LV3m8vyy4rmFidmGUdtcvlYmlVtzfnlVIWE_m8SaCE6IjDPfXH3u6eVstl24C2jA3SKKAQuhUO90gLlyf0Jo6Ae9UM2DICNp4pgbFT','thumb_IMG_8684.jpg'),(363,3,4,'IMG_8683.jpeg','uploads\\IMG_8683.jpeg',2710136,'image/jpeg','2025-09-14 13:39:52','gAAAAABoxsWo7HzCKnj6t98n6fS5Tcjz5sCnKGhsiC-UDApOTq3iiFPeSIt5jNnL2IzjTneeH_Paf0UpHLWzfRlg4UeeHsigRoC-zIJZ5A1QhLx_WmA30x11j0S2gYTNjFq01dBQTjwY','thumb_IMG_8683.jpg'),(364,3,4,'IMG_8682.jpeg','uploads\\IMG_8682.jpeg',2843108,'image/jpeg','2025-09-14 13:39:53','gAAAAABoxsWp_UV6--twTS1YSSjJ6TTwxMRnXb5cDIT-VCEVV6_G77wvTVT_ZxanyeoJKsoqHqyJYvgMJkZk5G2zXR_dhQWXfT6Tj8Z8BKjDxYWyGeTtSZ7v-N64q_LK3_ghSnlF_9Q0','thumb_IMG_8682.jpg'),(365,3,4,'IMG_8681.jpeg','uploads\\IMG_8681.jpeg',2746660,'image/jpeg','2025-09-14 13:39:53','gAAAAABoxsWpKl83Kq5IYKwOgSHO4Nxjxip_v_dkITDGrIEWn6E_2I4eQ_wl1j77oN_Uemdb1IuUDF6qeDyz-bwzoMHSQIp5ayIVWjiLIndeBMlPj9JPF4OYVhZ49h38ouetnMBpbdZF','thumb_IMG_8681.jpg'),(366,3,4,'IMG_8356.mov','uploads\\IMG_8356.mov',49275148,'video/quicktime','2025-09-14 13:47:59','gAAAAABoxsePyb8V3j0K45dDLp36KUXk_7JCvIFKAfBb40DalO5UQg_i1-FSx4WKYSwgpfLWrxwqbTthJlmXbI9xzobYEbq6n9FmO1XHtDcv-n_dtJxjOEx5hS_SoekJZObkbRHf49BZ','thumb_IMG_8356.jpg'),(367,3,4,'IMG_8337.jpeg','uploads\\IMG_8337.jpeg',2859640,'image/jpeg','2025-09-14 13:54:35','gAAAAABoxskbllX-aPAqcOOZ8SouXMd21eWJZQJKb2wlGUd0dgcTqj5ZtMnxjWXPljvkthGYZJjzWdi4Lgu3kTggt79x4HhHxo9RDzVN5xsHlDGEYIFMgtSZPKhpBQagQJJRr7It40Be','thumb_IMG_8337.jpg'),(368,3,4,'IMG_8355.mov','uploads\\IMG_8355.mov',148374668,'video/quicktime','2025-09-14 13:55:22','gAAAAABoxslKjsdz2wCAOKDPHkb60v4sV94CmBZ_HuQVpe6eTGrtykxiXpad-QW5ybRU62BgpAQeZyDDD65PVqpaZRnNC1VRs7YpikmokfM2nOPi7G4HX5JxtFjI0W9YR_3k5D_1raqj','thumb_IMG_8355.jpg'),(369,3,4,'IMG_8354.jpeg','uploads\\IMG_8354.jpeg',3618788,'image/jpeg','2025-09-14 13:55:24','gAAAAABoxslMyRs17j5ntZLAi5m6Q5Ct5z7EKNQq0inMbuR4A9xQxHN0VNYtWqtzeZQ4TObHvx6ifWWO39a8lzhJfKi5o8mhT91IW4nGMMyfpxNn_Dhnp_kmBhNLEf111uAlqARJpGSL','thumb_IMG_8354.jpg'),(370,3,4,'IMG_8352.jpeg','uploads\\IMG_8352.jpeg',3280676,'image/jpeg','2025-09-14 13:55:25','gAAAAABoxslNh9uOqOpzgoCdfJcce1sl26H5oIbW__f25tjhnQFmymD9_0sXgnKOnkafhd0E-nuyYOdQIimSiUkemr2a4C6ASPNCb7nUOS6BaeBwBh-KI01Kazt53IZLPmdSmjdxGjtO','thumb_IMG_8352.jpg'),(371,3,4,'IMG_8351.jpeg','uploads\\IMG_8351.jpeg',2922252,'image/jpeg','2025-09-14 13:55:26','gAAAAABoxslO0FraWk0OrjBKcc1QVPZh12NeapeB3CkD1DY4C8nuL75qQUEcLyb6CLkSUVXPs7MG2efDb1MGDQ04IngeneE62D2Dc7oDMBaCoRfg3LVv7TUJeaQpc4c0WkZ6-4NmnPw5','thumb_IMG_8351.jpg'),(372,3,4,'IMG_8349.jpeg','uploads\\IMG_8349.jpeg',2244364,'image/jpeg','2025-09-14 13:55:27','gAAAAABoxslP6dOR4MnouadGcdUEraQs6lrW6LE3SPPcL2ZwsfPKJOqChWhLAC7nrQfHug-AQN61BaRYM2MHafnluQrTHMpgwuxtKw5jZotgAD8K_LLxAFD0biCzZTWs1Ucz735dKWQ1','thumb_IMG_8349.jpg'),(373,3,5,'VID_20250914_222749.mp4','uploads\\VID_20250914_222749.mp4',98252664,'video/mp4','2025-09-14 17:06:12','gAAAAABoxvYEbsEa27bLvJRRXiM0zcSaJE4cN4g7P8ujLsEwZ-v1fF3nhHjw4r7-fW-ddiR4gcCf5fvQU2_dt4kSlcz5yBHUblmv6pUN6v31FUOTZnw5c5HcwRHc-Z3OfjYZjxM4HdRW','thumb_VID_20250914_222749.jpg'),(374,3,5,'IMG_9340.mov','uploads\\IMG_9340.mov',57865336,'video/quicktime','2025-09-14 17:08:47','gAAAAABoxvafcc5DLjycw7sN0K0qwNnU02cLI-hGMeyraf3p5mNNeL1Wcp3MjJQyhybsGBFzX2fW-NIw-W8PqlD_o7KJvDFWW-LGdxT2_Gf41RT-BL5VU6_Bc-fphvgYC9zrrHgdFDBb','thumb_IMG_9340.jpg'),(375,3,5,'IMG_9339.mov','uploads\\IMG_9339.mov',21114020,'video/quicktime','2025-09-14 17:08:51','gAAAAABoxvajbAUQwX537S4i9V39zhnkvci9RuAv__l6tirOijkB0hI-Zpp__zxrA2INoHw1FzZw6ODyL8jftXJ54RCchI7Zegn0q6UEyhJeAlonYlm8dAVH95koKVZCWB6glYCE2poJ','thumb_IMG_9339.jpg'),(376,3,5,'IMG_9338.mov','uploads\\IMG_9338.mov',33079524,'video/quicktime','2025-09-14 17:08:58','gAAAAABoxvaq_WE5IgKN8MWw_JPRCYdbCDtv0pJ-UHMd2pqAg4t3HICqh9sfUxPlxAGfZNqPn63HZ-V5MaG8MPdHb-JhYNUrdKCg6FBwSgO0bX6BVhBoEkjk48m0OERBbYlc8W7MHUbk','thumb_IMG_9338.jpg'),(377,3,5,'IMG_9337.mov','uploads\\IMG_9337.mov',30636684,'video/quicktime','2025-09-14 17:09:03','gAAAAABoxvav3f97Fk36bv3y_24CKQd_iAPYuBeQ5xtkJLSTvKAJG3C2MJLoqE-BLnR3X0Dare4Iy6LDb2rcg2nm_hAd6yTJWBUj7GO0_nMJNrCsT5pn7Hb_qwgen_wKGeeQSZP0Q7Tx','thumb_IMG_9337.jpg'),(378,3,5,'IMG_9340_1.mov','uploads\\IMG_9340_1.mov',57865228,'video/quicktime','2025-09-14 17:13:13','gAAAAABoxvepYYsfyUFxttpqGL-cj2JxnXTTWPEd2LSDIamcXcteQatCERhhvpTzCqzI1aq31siL4PKwKif7m9e50leCrTVglMQkOuIaoXZhVyskwAQMoiL6ixsB_P1TTqNUp1i8jdNX','thumb_IMG_9340_1.jpg'),(383,3,5,'video-output-BCD1A7C6-35E1-463F-81BE-916679D4A22A-1.mov','uploads\\video-output-BCD1A7C6-35E1-463F-81BE-916679D4A22A-1.mov',17254136,'video/quicktime','2025-09-14 19:48:38','gAAAAABoxxwW8c--GtXlLczkHt_SCNfKVXuAGbBZpoCJUR6zkT61CmhvbQR7mPZKl0XsHdQStnTO1E5wo1ZMV-PrbYObkMvuVe5zkmJicRIMQnNmritO1JrGMSl5VtB6r8CdJb-g4aXY','thumb_video-output-BCD1A7C6-35E1-463F-81BE-916679D4A22A-1.jpg'),(384,3,5,'video-output-C1F7ABCE-E368-48EE-A4FF-07F7DAE1C219-1.mov','uploads\\video-output-C1F7ABCE-E368-48EE-A4FF-07F7DAE1C219-1.mov',23433144,'video/quicktime','2025-09-14 19:48:45','gAAAAABoxxwdmWhj90uF_w7vM4ZzRwYGOTS2KiKYmsFNXe6aYAlOQ-m8nFM3IX6z0WOnJ4UHTf_B0f10Gn60vWxS9WGaWW0pMdjtG0MNzjZFmg8gyj7u9NdHyK64LXUHUzWSnSZDNSU2','thumb_video-output-C1F7ABCE-E368-48EE-A4FF-07F7DAE1C219-1.jpg'),(385,3,5,'IMG_8147.mov','uploads\\IMG_8147.mov',13283532,'video/quicktime','2025-09-14 19:48:46','gAAAAABoxxwe6UR2jljpXbRLBaaDq1S82rlcXocMTUoelVVujdate5bmuxBXc4dZSV_ugsakotMydYfa5kGCdbdjFoJUyyd20WGEVsN3SZ4R9SDyuXzhc7YyA-PUdHs3KpGVZSgR-Aut','thumb_IMG_8147.jpg'),(386,3,5,'IMG_8139.mov','uploads\\IMG_8139.mov',46628452,'video/quicktime','2025-09-14 19:48:52','gAAAAABoxxwkfF1tB9xk9MgrI6nKA-zi0YnDRhfvHKDR3YtJ1uLNE7NlCGdcSBKrX3x7VFXoRNTLj0Kyj5T7KapndofMHPHWD7ppORwSmQJhYWWbssOMgbeT6oq583N3Vo0d9nJSVHzx','thumb_IMG_8139.jpg'),(387,3,5,'IMG_8139_1.mov','uploads\\IMG_8139_1.mov',46628452,'video/quicktime','2025-09-14 19:48:57','gAAAAABoxxwpOQBbxsNLK88Z3nycx_ZMa2R6HykVWZCQVmEUfs881PCnqYt2tAweJQgzEOhyIoPMqK3-WC2ai7p7gUd4GrmcCgAKVgdrFY2miYV58mvR29wyhHfi7poM2TcT50Ir5CPQ','thumb_IMG_8139_1.jpg');
/*!40000 ALTER TABLE `file` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `folder`
--

DROP TABLE IF EXISTS `folder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `folder` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `folder_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `folder` (`id`),
  CONSTRAINT `folder_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `folder`
--

LOCK TABLES `folder` WRITE;
/*!40000 ALTER TABLE `folder` DISABLE KEYS */;
INSERT INTO `folder` VALUES (1,3,NULL,'MyPhone'),(2,3,1,'Iphone'),(3,3,2,'Backup'),(4,3,2,'Subscription'),(5,3,4,'... ');
/*!40000 ALTER TABLE `folder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification`
--

DROP TABLE IF EXISTS `notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notification` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `message` varchar(255) NOT NULL,
  `link` varchar(255) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `notification_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification`
--

LOCK TABLES `notification` WRITE;
/*!40000 ALTER TABLE `notification` DISABLE KEYS */;
INSERT INTO `notification` VALUES (1,3,'You shared \'IMG_8352.jpeg\' with Sujoy Das.',NULL,1,'2025-09-14 19:53:36'),(2,1,'\'Sujoy Das\' shared a file with you: \'IMG_8352.jpeg\'','/',1,'2025-09-14 19:53:36'),(3,3,'You shared \'IMG_8349.jpeg\' with Sujoy Das.',NULL,1,'2025-09-14 20:03:19'),(4,1,'\'Sujoy Das\' shared a file with you: \'IMG_8349.jpeg\'','/',1,'2025-09-14 20:03:19'),(5,3,'You shared \'IMG_8349.jpeg\' with Sujoy Das.',NULL,1,'2025-09-14 20:38:56'),(6,1,'\'Sujoy Das\' shared a file with you: \'IMG_8349.jpeg\'','/',1,'2025-09-14 20:38:56');
/*!40000 ALTER TABLE `notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `plan_id` int(11) NOT NULL,
  `amount` float NOT NULL,
  `status` varchar(50) NOT NULL,
  `txn_id` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `plan_id` (`plan_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`plan_id`) REFERENCES `plan` (`id`),
  CONSTRAINT `payment_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plan`
--

DROP TABLE IF EXISTS `plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `size_limit` bigint(20) NOT NULL,
  `price` float DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plan`
--

LOCK TABLES `plan` WRITE;
/*!40000 ALTER TABLE `plan` DISABLE KEYS */;
INSERT INTO `plan` VALUES (1,'Free',21474836480,0,9999);
/*!40000 ALTER TABLE `plan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription`
--

DROP TABLE IF EXISTS `subscription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subscription` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `plan_id` int(11) NOT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `plan_id` (`plan_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `subscription_ibfk_1` FOREIGN KEY (`plan_id`) REFERENCES `plan` (`id`),
  CONSTRAINT `subscription_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription`
--

LOCK TABLES `subscription` WRITE;
/*!40000 ALTER TABLE `subscription` DISABLE KEYS */;
INSERT INTO `subscription` VALUES (1,3,1,'2025-09-14 12:41:52','2125-08-21 12:41:52',1),(2,1,1,'2025-09-14 12:54:28','2125-08-21 12:54:28',1);
/*!40000 ALTER TABLE `subscription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password_hash` varchar(200) NOT NULL,
  `role` varchar(20) DEFAULT NULL,
  `plan_id` int(11) DEFAULT NULL,
  `used_storage` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `plan_id` (`plan_id`),
  CONSTRAINT `user_ibfk_1` FOREIGN KEY (`plan_id`) REFERENCES `plan` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'Sujoy Das','das.sujoy83@gmail.com','scrypt:32768:8:1$OCSYnDWkN2Pmlcos$4daf76d48dc006e1f64a62c58e6832d542c58ba6cd2c0cb449173e5bd59d2ca1924b512a7fe0dade379ed4a6fe1f29e04bfd1b1c147750e4b6bc6d34b661a30e','user',1,0),(2,'admin','admin@example.com','scrypt:32768:8:1$enS4rVMCsfj3L7KL$303429235641e011e8b73fa3cdf4da7a6b37bbd9dfd1b6c07d1e66e49aec283ff6a859fad9bcd5f77794892a0d0f99abef70340e9eb9bb76f57d9c9f869cd48b','admin',NULL,0),(3,'Sujoy Das','analyst.sujoydas@gmail.com','scrypt:32768:8:1$qpNkdg3XeLJb9q0Q$0f7a5dfbcd718e8ed2df1a7a8e1233e28677b0f8143c226a76a8a3c6330188bc8c018d2dc53c2ffa66ac65630d320dd9bd7c415db68151db7b221ee6c8810977','user',1,-3430799328);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_file_share`
--

DROP TABLE IF EXISTS `user_file_share`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_file_share` (
  `user_id` int(11) NOT NULL,
  `file_id` int(11) NOT NULL,
  `can_download` tinyint(1) NOT NULL,
  `can_reshare` tinyint(1) NOT NULL,
  `can_copy` tinyint(1) NOT NULL,
  PRIMARY KEY (`user_id`,`file_id`),
  KEY `file_id` (`file_id`),
  CONSTRAINT `user_file_share_ibfk_1` FOREIGN KEY (`file_id`) REFERENCES `file` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_file_share_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_file_share`
--

LOCK TABLES `user_file_share` WRITE;
/*!40000 ALTER TABLE `user_file_share` DISABLE KEYS */;
INSERT INTO `user_file_share` VALUES (1,372,1,0,0);
/*!40000 ALTER TABLE `user_file_share` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_folder_share`
--

DROP TABLE IF EXISTS `user_folder_share`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_folder_share` (
  `user_id` int(11) NOT NULL,
  `folder_id` int(11) NOT NULL,
  `can_download` tinyint(1) NOT NULL,
  `can_reshare` tinyint(1) NOT NULL,
  `can_copy` tinyint(1) NOT NULL,
  PRIMARY KEY (`user_id`,`folder_id`),
  KEY `folder_id` (`folder_id`),
  CONSTRAINT `user_folder_share_ibfk_1` FOREIGN KEY (`folder_id`) REFERENCES `folder` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_folder_share_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_folder_share`
--

LOCK TABLES `user_folder_share` WRITE;
/*!40000 ALTER TABLE `user_folder_share` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_folder_share` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-15 11:11:21
