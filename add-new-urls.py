from scrape import BBBScraper
from sys import platform
from includes.proxies import getProxy
from multiprocessing import Queue, Process
import argparse, time
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(handlers=[
    logging.FileHandler("logs/scrape_with_errors.py.log"),
    logging.StreamHandler()
], format='%(asctime)s Process ID %(process)d: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)

if __name__ == "__main__":
    scraper = BBBScraper()

    companies = scraper.db.queryArray(
        f"SELECT company_id, url from company where status = 'new' order by company_id LIMIT 1000")
    if companies:
        for company in companies:
            try:
                scraper.scrape_url(company['url'], scrape_reviews_and_complaints=True)
            except Exception as e:
                logging.error("scrape_url exception: " + str(e))

    scraper.addNewUrls()
