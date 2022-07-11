CREATE DATABASE IF NOT EXISTS bbb;
USE bbb;

CREATE TABLE IF NOT EXISTS `company` (
  `company_id` int NOT NULL AUTO_INCREMENT,
  `company_name` varchar(255) NOT NULL,
  `url` varchar(500) NOT NULL,
  `logo` varchar(255) DEFAULT NULL,
  `categories` varchar(255) DEFAULT NULL,
  `phone` varchar(18) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `website` varchar(500) DEFAULT NULL,
  `is_accredited` tinyint(1) DEFAULT NULL,
  `rating` varchar(2) DEFAULT NULL,
  `working_hours` varchar(500) DEFAULT NULL,
  `number_of_stars` decimal(2,1) DEFAULT NULL,
  `number_of_reviews` int DEFAULT NULL,
  `overview` text DEFAULT NULL,
  `products_and_services` text DEFAULT NULL,
  `business_started` varchar(255) DEFAULT NULL,
  `business_incorporated` varchar(255) DEFAULT NULL,
  `type_of_entity` varchar(255) DEFAULT NULL,
  `number_of_employees` varchar(255) DEFAULT NULL,
  `business_management` text DEFAULT NULL,
  `contact_information` text DEFAULT NULL,
  `customer_contact` text DEFAULT NULL,
  `fax_numbers` text DEFAULT NULL,
  `serving_area` text DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `date_updated` datetime DEFAULT NULL,
  `status` varchar(7) DEFAULT NULL,
  `log` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `review` (
  `review_id` int NOT NULL AUTO_INCREMENT,
  `company_id` int NOT NULL,
  `review_date` date DEFAULT NULL,
  `username` varchar(255) NOT NULL,
  `review_text` text,
  `review_rating` decimal(2,1) DEFAULT NULL,
  `company_response_text` text DEFAULT NULL,
  `company_response_date` date DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `date_updated` datetime DEFAULT NULL,
  `status` varchar(7) DEFAULT NULL,
  `log` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`review_id`),
  KEY `company_id` (`company_id`),
  CONSTRAINT `review_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=78366 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `complaint` (
  `complaint_id` int NOT NULL AUTO_INCREMENT,
  `company_id` int NOT NULL,
  `complaint_type` varchar(255) DEFAULT NULL,
  `complaint_date` date DEFAULT NULL,
  `complaint_text` text DEFAULT NULL,
  `company_response_text` text DEFAULT NULL,
  `company_response_date` date DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `date_updated` datetime DEFAULT NULL,
  `status` varchar(7) DEFAULT NULL,
  `log` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`complaint_id`),
  KEY `company_id` (`company_id`),
  CONSTRAINT `complaint_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company` (`company_id`)
) ENGINE=InnoDB AUTO_INCREMENT=78366 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;