from scrape import BBBScraper
from sys import platform
from includes.proxies import getProxy
from multiprocessing import Queue, Process
import argparse, time
import logging
from logging.handlers import RotatingFileHandler

rfh = RotatingFileHandler(
    filename="logs/add-new-urls.py.log", 
    mode='a',
    maxBytes=20*1024*1024,
    backupCount=1,
    delay=0,
    encoding=None
)
rfh.setFormatter(logging.Formatter('%(asctime)s Process ID %(process)d: %(message)s'))
rfh.setLevel(level=logging.DEBUG)

root = logging.getLogger('root')
root.setLevel(logging.INFO)
root.addHandler(rfh)

if __name__ == "__main__":
    
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
    