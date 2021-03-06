# BBBScraper

## Installation Guide

1. If need to use mariaDB, install connector dependency first from here: https://mariadb.com/docs/clients/mariadb-connectors/connector-c/install/
2. Install required libraries using "pip install -r requirements.txt"

3. For selenium to work, you will need to have chromedriver in your path. Download chromedriver from https://chromedriver.chromium.org/

4. Use schema.sql to create the database and tables

5. In config.py, set the credentials according for your mysql server

6. The main script for CLI is BBBScrapper. Using "python BBBScrapper --h" will show you how to run it

7. During the bulk-scrape, the script will produce a backup file for efficiency named last_scrape_info.json
   If for some reason the script stops during the scrape, on restart the script will read from these files and continue from where it left off.
   If you wish to start from the beginning, simply delete this file.

## API Server

Run api_server.py to start the server.

### Endpoints:

[GET] /api/v1/regrab-company

parameters: id (id of the company), webhookUrl (url to post after finishing scraping)

[GET] /api/v1/regrab-review

parameters: id (id of the review), webhookUrl (url to post after finishing scraping)

[GET] /api/v1/regrab-complaint

parameters: id (id of the complaint), webhookUrl (url to post after finishing scraping)
