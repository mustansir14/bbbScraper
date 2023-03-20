from scrape import BBBScraper
from sys import platform
from includes.proxies import getProxy
from multiprocessing import Queue, Process
import argparse, time
import logging

if __name__ == "__main__":
    
    logging.basicConfig(handlers=[
        logging.FileHandler("logs/add-new-urls.py.log"),
        logging.StreamHandler()
    ], format='%(asctime)s Process ID %(process)d: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    
    sitemap_urls = ["https://www.bbb.org/sitemap-accredited-business-profiles-index.xml", "https://www.bbb.org/sitemap-business-profiles-index.xml"]
    
    scraper = BBBScraper()
    
    start = time.time();
    scanAgain = 24*3600
    
    while time.time() - start < scanAgain:
        companies = scraper.db.queryArray(f"SELECT company_id, url from company where status = 'new' LIMIT 1000")
        if not companies:
            break
            
        for company in companies:
            if time.time() - start > scanAgain:
                break
                
            scraper.scrape_url(company['url'], scrape_reviews_and_complaints=True)
            
    scraper.addNewUrls()
    