-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Хост: 65.109.70.91
-- Время создания: Ноя 17 2023 г., 10:40
-- Версия сервера: 10.9.7-MariaDB
-- Версия PHP: 8.1.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `scraper_bbb_mustansir`
--

DELIMITER $$
--
-- Функции
--
CREATE DEFINER=`remote`@`%` FUNCTION `getDomain` (`website` TEXT) RETURNS TEXT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci  begin
	declare domain text default null;
    
	if website is not null then
    	set domain = sanitize_url(website);
    	set domain = regexp_replace(domain,concat("https?://(www", char(92), ".)?"), "");
        set domain = regexp_replace(domain, "/.*", "");
        if instr(domain, ".") = 0 then
        	set domain = null;
        end if;
    end if;
    
    return domain;
end$$

CREATE DEFINER=`remote`@`%` FUNCTION `sanitize_url` (`url` TEXT) RETURNS TEXT CHARSET ascii COLLATE ascii_general_ci  begin
	# https://github.com/php/php-src/blob/master/ext/filter/sanitizing_filters.c#L308
    # LOWALPHA HIALPHA DIGIT SAFE EXTRA NATIONAL PUNCTUATION RESERVED;
    # SAFE        "$-_.+"
	# EXTRA       "!*'(),"
	# NATIONAL    "{}|\\^~[]`"
	# PUNCTUATION "<>#%\""
	# RESERVED    ";/?:@&="
    return regexp_replace(url, concat(
        "[^",
        "a-zA-Z0-9",
        
        char(92), "$", char(92), "-", "_", char(92), ".", char(92), "+",
        
        char(92), "!", char(92), "*", char(92), "'", char(92), "(", char(92), ")", ",",
        
        char(92), "{", char(92), "}", char(92), "|", char(92), char(92), "^", char(92), "~", 
        char(92), "[", char(92), "]", char(92), "`", 
        
        char(92), "<", char(92), ">", char(92), "#", char(92), "%", '"', 
        
        char(92), ";", char(92), "/", char(92), "?", char(92), ":", char(92), "@", 
        char(92), "&", char(92), "=", 
        
        "]"
    ), "");
end$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Структура таблицы `company`
--

CREATE TABLE `company` (
  `company_id` int(11) NOT NULL,
  `version` int(11) DEFAULT 1,
  `company_name` varchar(255) DEFAULT NULL,
  `alternate_business_name` varchar(500) DEFAULT NULL,
  `url` varchar(500) NOT NULL,
  `logo` varchar(255) DEFAULT NULL,
  `categories` text DEFAULT NULL,
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
  `products_and_services` longtext DEFAULT NULL,
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
  `log` longtext DEFAULT NULL,
  `half_scraped` tinyint(1) DEFAULT 0,
  `exists_on_cb` tinyint(4) NOT NULL DEFAULT 0,
  `exists_on_cb_comment` text DEFAULT NULL,
  `domain` varchar(150) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Триггеры `company`
--
DELIMITER $$
CREATE TRIGGER `company_before_insert` BEFORE INSERT ON `company` FOR EACH ROW begin
	if new.website is not null then
    	set new.domain = getDomain(new.website);
    end if;
end
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `company_before_update` BEFORE UPDATE ON `company` FOR EACH ROW begin
	if new.website is not null then
    	set new.domain = getDomain(new.website);
    end if;
end
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Структура таблицы `complaint`
--

CREATE TABLE `complaint` (
  `complaint_id` int(11) NOT NULL,
  `company_id` int(11) NOT NULL,
  `company_half_scraped` int(11) DEFAULT NULL,
  `company_exists_on_cb` tinyint(4) NOT NULL DEFAULT 0,
  `complaint_type` varchar(255) DEFAULT NULL,
  `complaint_date` date DEFAULT NULL,
  `complaint_date_year` int(11) DEFAULT NULL,
  `complaint_text` text DEFAULT NULL,
  `complaint_text_hash` varchar(32) DEFAULT NULL,
  `company_response_text` text DEFAULT NULL,
  `company_response_date` date DEFAULT NULL,
  `source_code` longtext DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `date_updated` datetime DEFAULT NULL,
  `status` varchar(7) DEFAULT NULL,
  `log` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Триггеры `complaint`
--
DELIMITER $$
CREATE TRIGGER `complaint_before_insert` BEFORE INSERT ON `complaint` FOR EACH ROW BEGIN
	set new.complaint_text_hash = md5(concat(new.company_id,new.complaint_text));
    set new.complaint_date_year = year(new.complaint_date);
    set new.company_half_scraped =(select half_scraped from company where company.company_id = new.company_id);
    set new.company_exists_on_cb =(select exists_on_cb from company where company.company_id = new.company_id);
end
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `complaint_before_update` BEFORE UPDATE ON `complaint` FOR EACH ROW BEGIN
	set new.complaint_text_hash = md5(concat(new.company_id,new.complaint_text));
    set new.complaint_date_year = year(new.complaint_date);
    set new.company_half_scraped =(select half_scraped from company where company.company_id = new.company_id);
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
  `review_date_year` int(11) DEFAULT NULL,
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
  `log` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Триггеры `review`
--
DELIMITER $$
CREATE TRIGGER `review_before_insert` BEFORE INSERT ON `review` FOR EACH ROW BEGIN
	SET NEW.review_text_hash = md5(concat(new.company_id,NEW.review_text));
    set new.review_date_year = year(new.review_date);
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `review_before_update` BEFORE UPDATE ON `review` FOR EACH ROW BEGIN
	SET NEW.review_text_hash = md5(concat(new.company_id,NEW.review_text));
    set new.review_date_year = year(new.review_date);
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Структура таблицы `settings`
--

CREATE TABLE `settings` (
  `name` varchar(100) NOT NULL,
  `value` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `urls_pages`
--

CREATE TABLE `urls_pages` (
  `id_urls_pages` int(11) NOT NULL,
  `url_urls_pages` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `urls_sitemap`
--

CREATE TABLE `urls_sitemap` (
  `id_urls_sitemap` int(11) NOT NULL,
  `url_urls_sitemap` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `company`
--
ALTER TABLE `company`
  ADD PRIMARY KEY (`company_id`),
  ADD UNIQUE KEY `url` (`url`) USING BTREE,
  ADD KEY `company_name` (`company_name`),
  ADD KEY `date_updated` (`date_updated`),
  ADD KEY `for_stats` (`date_updated`,`status`) USING BTREE,
  ADD KEY `half_scraped` (`half_scraped`),
  ADD KEY `exists_on_cb` (`exists_on_cb`),
  ADD KEY `status` (`status`),
  ADD KEY `rating` (`rating`),
  ADD KEY `date_created` (`date_created`),
  ADD KEY `domain` (`domain`);

--
-- Индексы таблицы `complaint`
--
ALTER TABLE `complaint`
  ADD PRIMARY KEY (`complaint_id`),
  ADD UNIQUE KEY `complaint_text_hash` (`complaint_text_hash`),
  ADD KEY `company_id` (`company_id`),
  ADD KEY `for_stats` (`date_updated`,`status`),
  ADD KEY `complaint_date_year` (`complaint_date_year`),
  ADD KEY `company_half_scraped` (`company_half_scraped`,`complaint_date_year`,`company_exists_on_cb`) USING BTREE;

--
-- Индексы таблицы `review`
--
ALTER TABLE `review`
  ADD PRIMARY KEY (`review_id`),
  ADD UNIQUE KEY `review_text_hash` (`review_text_hash`) USING BTREE,
  ADD KEY `company_id` (`company_id`),
  ADD KEY `for_stats` (`date_updated`,`status`),
  ADD KEY `review_date_year` (`review_date_year`);

--
-- Индексы таблицы `settings`
--
ALTER TABLE `settings`
  ADD UNIQUE KEY `name` (`name`);

--
-- Индексы таблицы `urls_pages`
--
ALTER TABLE `urls_pages`
  ADD PRIMARY KEY (`id_urls_pages`),
  ADD UNIQUE KEY `url_urls_pages` (`url_urls_pages`);

--
-- Индексы таблицы `urls_sitemap`
--
ALTER TABLE `urls_sitemap`
  ADD PRIMARY KEY (`id_urls_sitemap`),
  ADD UNIQUE KEY `url_urls_sitemap` (`url_urls_sitemap`);

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
-- AUTO_INCREMENT для таблицы `urls_pages`
--
ALTER TABLE `urls_pages`
  MODIFY `id_urls_pages` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `urls_sitemap`
--
ALTER TABLE `urls_sitemap`
  MODIFY `id_urls_sitemap` int(11) NOT NULL AUTO_INCREMENT;

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `complaint`
--
ALTER TABLE `complaint`
  ADD CONSTRAINT `complaint_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company` (`company_id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Ограничения внешнего ключа таблицы `review`
--
ALTER TABLE `review`
  ADD CONSTRAINT `review_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `company` (`company_id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
