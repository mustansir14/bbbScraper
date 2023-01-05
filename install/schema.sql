-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Хост: 65.109.70.91
-- Время создания: Янв 05 2023 г., 14:55
-- Версия сервера: 10.9.4-MariaDB
-- Версия PHP: 8.1.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

--
-- База данных: `scraper_bbb_mustansir`
--

-- --------------------------------------------------------

--
-- Структура таблицы `company`
--

CREATE TABLE `company` (
  `company_id` int(11) NOT NULL,
  `version` int(11) DEFAULT 1,
  `company_name` varchar(255) NOT NULL,
  `alternate_business_name` varchar(500) DEFAULT NULL,
  `url` varchar(500) NOT NULL,
  `logo` varchar(255) DEFAULT NULL,
  `categories` varchar(255) DEFAULT NULL,
  `phone` text DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `street_address` varchar(256) DEFAULT NULL,
  `address_locality` varchar(256) DEFAULT NULL,
  `address_region` varchar(256) DEFAULT NULL,
  `postal_code` varchar(256) DEFAULT NULL,
  `country` varchar(2) DEFAULT NULL,
  `website` text DEFAULT NULL,
  `hq` tinyint(1) DEFAULT NULL,
  `is_accredited` tinyint(1) DEFAULT NULL,
  `bbb_file_opened` date DEFAULT NULL,
  `years_in_business` varchar(255) DEFAULT NULL,
  `accredited_since` date DEFAULT NULL,
  `rating` varchar(2) DEFAULT NULL,
  `original_working_hours` text DEFAULT NULL,
  `working_hours` varchar(500) DEFAULT NULL,
  `number_of_stars` decimal(2,1) DEFAULT NULL,
  `number_of_reviews` int(11) DEFAULT NULL,
  `number_of_complaints` int(11) DEFAULT NULL,
  `overview` text DEFAULT NULL,
  `products_and_services` text DEFAULT NULL,
  `business_started` varchar(255) DEFAULT NULL,
  `business_incorporated` varchar(255) DEFAULT NULL,
  `type_of_entity` varchar(255) DEFAULT NULL,
  `number_of_employees` varchar(255) DEFAULT NULL,
  `original_business_management` text DEFAULT NULL,
  `business_management` text DEFAULT NULL,
  `original_contact_information` text DEFAULT NULL,
  `contact_information` text DEFAULT NULL,
  `original_customer_contact` text DEFAULT NULL,
  `customer_contact` text DEFAULT NULL,
  `fax_numbers` text DEFAULT NULL,
  `additional_phones` text DEFAULT NULL,
  `additional_websites` text DEFAULT NULL,
  `additional_faxes` text DEFAULT NULL,
  `serving_area` text DEFAULT NULL,
  `payment_methods` text DEFAULT NULL,
  `referral_assistance` text DEFAULT NULL,
  `refund_and_exchange_policy` text DEFAULT NULL,
  `business_categories` text DEFAULT NULL,
  `facebook` varchar(500) DEFAULT NULL,
  `instagram` varchar(500) DEFAULT NULL,
  `twitter` varchar(500) DEFAULT NULL,
  `pinterest` varchar(500) DEFAULT NULL,
  `linkedin` varchar(500) DEFAULT NULL,
  `source_code` longtext DEFAULT NULL,
  `source_code_details` longtext DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `date_updated` datetime DEFAULT NULL,
  `status` varchar(7) DEFAULT NULL,
  `log` varchar(255) DEFAULT NULL,
  `half_scraped` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `complaint`
--

CREATE TABLE `complaint` (
  `complaint_id` int(11) NOT NULL,
  `company_id` int(11) NOT NULL,
  `complaint_type` varchar(255) DEFAULT NULL,
  `complaint_date` date DEFAULT NULL,
  `complaint_text` text DEFAULT NULL,
  `complaint_text_hash` varchar(32) DEFAULT NULL,
  `company_response_text` text DEFAULT NULL,
  `company_response_date` date DEFAULT NULL,
  `source_code` longtext DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `date_updated` datetime DEFAULT NULL,
  `status` varchar(7) DEFAULT NULL,
  `log` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Триггеры `complaint`
--
DELIMITER $$
CREATE TRIGGER `complaint_before_insert` BEFORE INSERT ON `complaint` FOR EACH ROW BEGIN
	set new.complaint_text_hash = md5(new.complaint_text);
end
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `complaint_before_update` BEFORE UPDATE ON `complaint` FOR EACH ROW BEGIN
	set new.complaint_text_hash = md5(new.complaint_text);
end
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Структура таблицы `review`
--

CREATE TABLE `review` (
  `review_id` int(11) NOT NULL,
  `company_id` int(11) NOT NULL,
  `review_date` date DEFAULT NULL,
  `username` varchar(255) NOT NULL,
  `review_text` text DEFAULT NULL,
  `review_text_hash` varchar(32) DEFAULT NULL,
  `review_rating` decimal(2,1) DEFAULT NULL,
  `company_response_text` text DEFAULT NULL,
  `company_response_date` date DEFAULT NULL,
  `source_code` longtext DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `date_updated` datetime DEFAULT NULL,
  `status` varchar(7) DEFAULT NULL,
  `log` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Триггеры `review`
--
DELIMITER $$
CREATE TRIGGER `review_before_insert` BEFORE INSERT ON `review` FOR EACH ROW BEGIN
	SET NEW.review_text_hash = md5(NEW.review_text);
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `review_before_update` BEFORE UPDATE ON `review` FOR EACH ROW BEGIN
	SET NEW.review_text_hash = md5(NEW.review_text);
END
$$
DELIMITER ;

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `company`
--
ALTER TABLE `company`
  ADD PRIMARY KEY (`company_id`),
  ADD KEY `company_name` (`company_name`),
  ADD KEY `url` (`url`);

--
-- Индексы таблицы `complaint`
--
ALTER TABLE `complaint`
  ADD PRIMARY KEY (`complaint_id`),
  ADD UNIQUE KEY `complaint_text_hash` (`complaint_text_hash`),
  ADD KEY `company_id` (`company_id`);

--
-- Индексы таблицы `review`
--
ALTER TABLE `review`
  ADD PRIMARY KEY (`review_id`),
  ADD UNIQUE KEY `review_text_hash` (`review_text_hash`) USING BTREE,
  ADD KEY `company_id` (`company_id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `company`
--
ALTER TABLE `company`
  MODIFY `company_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `complaint`
--
ALTER TABLE `complaint`
  MODIFY `complaint_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `review`
--
ALTER TABLE `review`
  MODIFY `review_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `complaint`
--
ALTER TABLE `complaint`
  ADD CONSTRAINT `complaint_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company` (`company_id`);

--
-- Ограничения внешнего ключа таблицы `review`
--
ALTER TABLE `review`
  ADD CONSTRAINT `review_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company` (`company_id`);
COMMIT;
